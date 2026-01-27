"""Measurement UI pane.

Provides `MeasureApp` which displays incoming (x,y,z) measurement points
in a 3D plot and stores them to timestamped CSV files under `measurements/`.

This refactor extracts plot and file initialization into helpers and adds
safer file I/O with encoding and basic error handling.
"""

import os
from datetime import datetime
from tkinter import Button, Frame

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm  # Import colormap utilities
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import parameters


class MeasureApp:
    def __init__(
        self,
        master,
        write_command,
        return_to_main,
        simulate=False,
        start_x=None,
        start_y=None,
        max_x=None,
        max_y=None,
    ):
        """Create MeasureApp.

        master: parent widget
        write_command: callable to send commands to device
        return_to_main: callable to switch UI back to main view
        simulate: if True, send simulated MEASURE command
        """
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main
        self.is_active = True
        self.simulate = simulate

        # Create a frame to hold the widgets
        self.frame = Frame(master)
        self.frame.pack()

        # Create a Back button to return to the main interface
        self.btn_back = Button(
            self.frame, text="Close", command=self.wrapper_return_to_main
        )
        self.btn_back.pack(anchor="w", padx=10, pady=10)

        # Create a Reset Rotation button to reset the 3D plot rotation
        self.btn_reset_rotation = Button(
            self.frame, text="Reset Rotation", command=self.reset_rotation
        )
        self.btn_reset_rotation.pack(anchor="w", padx=10, pady=10)
        self.btn_reset_rotation.pack_forget()  # Initially hide the Reset Rotation button

        # Initialize plotting and file storage
        self._init_plot()
        self._create_measurement_file()

        # Start the measurement process (only if write_command is callable)
        try:
            cmd = "MEASURE SIMULATE" if self.simulate else "MEASURE"
            if callable(self.write_command):
                self.write_command(cmd)
            else:
                print(f"MeasureApp: write_command not set, skipping send: {cmd}")
        except Exception as e:
            print(f"MeasureApp: error sending command '{cmd}': {e}")

        # measurement file created by _create_measurement_file

        # Bind the Escape key on the toplevel so it can be unbound cleanly
        try:
            toplevel = self.frame.winfo_toplevel()
            toplevel.bind_all("<Escape>", lambda event: self.wrapper_return_to_main())
        except Exception:
            try:
                self.master.bind_all(
                    "<Escape>", lambda event: self.wrapper_return_to_main()
                )
            except Exception:
                pass

        # Parameters are read on-demand via the global accessor

        # Prefer explicit constructor values; fall back to global accessor
        try:
            self.start_x = (
                start_x
                if start_x is not None
                else parameters.get_parameter("startX", int, 0)
            )
            self.start_y = (
                start_y
                if start_y is not None
                else parameters.get_parameter("startY", int, 0)
            )
            self.max_x = (
                max_x
                if max_x is not None
                else parameters.get_parameter("maxX", int, 200)
            )
            self.max_y = (
                max_y
                if max_y is not None
                else parameters.get_parameter("maxY", int, 200)
            )
        except Exception:
            self.start_x = 0
            self.start_y = 0
            self.max_x = 200
            self.max_y = 200

    def wrapper_return_to_main(self):
        # Set is_active to False and return to the main interface
        self.is_active = False
        # Unbind escape handler to avoid leaking handlers
        try:
            toplevel = self.frame.winfo_toplevel()
            toplevel.unbind_all("<Escape>")
        except Exception:
            try:
                self.master.unbind_all("<Escape>")
            except Exception:
                pass
        self.return_to_main()

    def update_data(self, message):
        # Safety check to ensure the object is still active
        if not hasattr(self, "is_active") or not self.is_active:
            return False

        # keep parameter-backed attrs up to date (parameters may arrive asynchronously)
        try:
            self._refresh_parameters()
        except Exception:
            pass

        # Update the Parameter interface with new data
        data = message.split(",")

        # Handle DONE message
        if len(data) > 1 and data[1] == "DONE":
            print("Measurement completed")
            self.wrapper_return_to_main()
            return True

        try:
            x, y, z = int(data[1]), int(data[2]), int(data[3])
        except (IndexError, ValueError) as e:
            print(f"Error parsing data: {e}, \n{message}")
            return False

        # Append the data to the file (safe write)
        try:
            with open(
                self.measurement_file_path, "a", encoding="utf-8", newline=""
            ) as file:
                file.write(f"{x},{y},{z}\n")
        except Exception as e:
            print(f"Warning: failed to write measurement to file: {e}")

        # Update the plot data buffers
        prev_y = getattr(self, "_last_y", None)
        self.x_data.append(x)
        self.y_data.append(y)
        self.z_data.append(z)

        # Trigger redraw when Y changes from previous point (row change)
        if prev_y is not None and y != prev_y:
            self.redraw_plot()

        # remember last seen y for next update
        self._last_y = y

    def _refresh_parameters(self):
        """Refresh parameter-backed attributes from the master parameter store."""
        # refresh typed values using the global parameters accessor
        try:
            self.start_x = parameters.get_parameter("startX", int, self.start_x)
            self.start_y = parameters.get_parameter("startY", int, self.start_y)
            self.max_x = parameters.get_parameter("maxX", int, self.max_x)
            self.max_y = parameters.get_parameter("maxY", int, self.max_y)
        except Exception:
            pass

    def _deferred_parameter_init(self, attempt, max_attempts=6):
        """Try a few times (via `after`) to pick up parameters that arrive after UI creation."""
        try:
            self._refresh_parameters()
        except Exception:
            pass
        # Deferred retries removed: parameters should be read on-demand.
        return

    def redraw_plot(self):
        # Safety check to ensure the object is still active and has required attributes
        if not hasattr(self, "is_active") or not self.is_active:
            return
        if not hasattr(self, "ax") or not hasattr(self, "canvas"):
            return

        # Clear the plot and redraw
        self.ax.clear()
        self.ax.set_xlim(0, 200)
        self.ax.set_ylim(0, 200)
        self.ax.set_zlim(0, 0xFFFF)

        # Check if there is enough data to create a surface
        if len(self.x_data) > 2 and len(self.y_data) > 2 and len(self.z_data) > 2:
            # Prepare data for the 3D plot
            x = np.array(self.x_data)
            y = np.array(self.y_data)
            z = np.array(self.z_data)

            # Plot the triangular surface with the new data
            self.ax.plot_trisurf(x, y, z, cmap=cm.coolwarm, linewidth=0.2)

        # Redraw the canvas
        self.canvas.draw()

    def reset_rotation(self):
        # Reset the rotation of the 3D plot to its initial state
        self.ax.view_init(
            elev=self.initial_elev, azim=self.initial_azim
        )  # Reset to initial elevation and azimuthal angles
        self.canvas.draw()
        self.btn_reset_rotation.pack_forget()  # Hide the Reset Rotation button after resetting

    def on_plot_hover(self, event):
        # Show the Reset Rotation button only if the plot has been rotated
        if self.ax.elev != self.initial_elev or self.ax.azim != self.initial_azim:
            self.btn_reset_rotation.pack(anchor="w", padx=10, pady=10)

    def _init_plot(self):
        """Initialize Matplotlib 3D figure, axes and the Tk canvas."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.x_data = []
        self.y_data = []
        self.z_data = []

        # Store the initial rotation state
        self.initial_elev = self.ax.elev
        self.initial_azim = self.ax.azim

        # Embed the plot in a Tkinter canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.canvas.mpl_connect("motion_notify_event", self.on_plot_hover)
        self.redraw_plot()

    def _create_measurement_file(self):
        """Create measurements folder and open a timestamped CSV file.

        If the file already exists, leave it (append mode will be used).
        """
        folder = os.path.join(os.getcwd(), "measurements")
        try:
            os.makedirs(folder, exist_ok=True)
        except Exception as e:
            print(f"Warning: could not create measurements folder: {e}")

        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(folder, f"measurement_{ts}.csv")
        self.measurement_file_path = path

        # create file with header if not exists
        if not os.path.exists(self.measurement_file_path):
            try:
                with open(
                    self.measurement_file_path, "w", encoding="utf-8", newline=""
                ) as f:
                    f.write("x,y,z\n")
            except Exception as e:
                print(f"Warning: could not create measurement file: {e}")
