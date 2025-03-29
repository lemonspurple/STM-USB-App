from tkinter import Frame, Button
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import config_utils
import os
import sys


class TunnelApp:
    def __init__(
        self, master, write_command, return_to_main, target_adc, tolerance_adc
    ):

        # Initialize TunnelApp with callbacks and settings
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main
        self.is_active = True
        self.target_adc = target_adc
        self.tolerance_adc = tolerance_adc

        # Create a frame to hold the widgets
        self.frame = Frame(master)
        self.frame.pack()

        # Create a frame for the buttons
        self.button_frame = Frame(self.frame)
        self.button_frame.pack(fill="x", pady=10)

        # Create a Back button to return to the main interface
        self.btn_back = Button(
            self.button_frame, text="Stop", command=self.wrapper_return_to_main
        )
        self.btn_back.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Create a Restart button to restart the TunnelApp
        self.btn_restart = Button(
            self.button_frame, text="Restart", command=self.restart
        )
        self.btn_restart.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        # Initialize the plot
        self.tunnel_counts = float(
            config_utils.get_config("TUNNEL", "tunnelcounts", 200)
        )
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # Initialize data lists
        self.adc_data = []
        self.z_data = []
        self.colors = []

        # Start the measurement process with the read tunnelcounts value
        self.write_command(f"TUNNEL,{int(self.tunnel_counts)}")

    def update_adc_limits(self, target_adc, limit_adc):
        self.target_adc = target_adc
        self.limit_adc = limit_adc

    def wrapper_return_to_main(self):
        # Set is_active to False and return to the main interface
        self.is_active = False
        self.return_to_main()

    def restart(self):
        # Clear the plot data
        self.clear_plot_data()
        # Restart the TunnelApp
        self.frame.destroy()
        self.__init__(
            self.master,
            self.write_command,
            self.return_to_main,
            self.target_adc,
            self.tolerance_adc,
        )
        print(f"Tolerance ADC: {self.tolerance_adc}")

    def clear_plot_data(self):
        # Clear the plot data
        self.adc_data = []
        self.z_data = []
        self.colors = []

    def update_data(self, message):
        if not hasattr(self, "adc_plot"):
            # Initialize plot elements
            (self.adc_plot,) = self.ax.plot([], [], "o", label="Tunnel")
            (self.z_plot,) = self.ax.plot([], [], "x", label="DAC Z")
            self.limit_hi_line = self.ax.axhline(
                y=self.target_adc + self.tolerance_adc,
                color="orange",
                linestyle="--",
                label="Limit hi",
            )
            self.limit_lo_line = self.ax.axhline(
                y=self.target_adc - self.tolerance_adc,
                color="orange",
                linestyle="--",
                label="Limit Lo",
            )

        # Update the plot with new data
        data = message.split(",")
        try:
            if data[0] == "TUNNEL":
                flag, adc, z = int(data[1]), int(data[2]), int(data[3])
            else:
                return False
        except Exception as e:
            print(f"Error: {e}, \n{message}")
            return False

        self.adc_data.append(adc)
        self.z_data.append(z)
        self.colors.append("red" if flag == 0 else "green")
        self.redraw_plot()

    def redraw_plot(self):
        # Clear the plot and redraw
        self.ax.clear()
        self.ax.scatter(
            range(len(self.adc_data)),
            self.adc_data,
            c=self.colors,
            marker="o",
            label="Tunnel",
        )
        self.ax.scatter(
            range(len(self.z_data)),
            self.z_data,
            c="black",
            marker="x",
            label="DAC Z",
        )
        self.ax.set_xlim(
            0, max(100, len(self.adc_data))
        )  # Adjust x-axis limit based on data length

        self.ax.axhline(
            y=self.target_adc + self.tolerance_adc,
            color="orange",
            linestyle="--",
            label="Limit hi",
        )
        self.ax.axhline(
            y=self.target_adc - self.tolerance_adc,
            color="orange",
            linestyle="--",
            label="Limit Lo",
        )
        self.ax.set_xlim(0, self.tunnel_counts)
        self.ax.set_ylim(-0x8000, 0x7FFF)  # Set y-axis limit to int16_t range
        self.ax.set_xlabel("Counter")
        self.ax.set_ylabel("ADC and DAC Z")
        self.ax.set_title("Tunnel Current ADC and DAC Z")
        self.ax.legend()

        # Adjust margins
        self.fig.subplots_adjust(left=0.2, right=0.95, top=0.9, bottom=0.1)

        # Redraw the canvas
        self.canvas.draw()
