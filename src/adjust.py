from tkinter import VERTICAL, Button, Label, LabelFrame, Scale, messagebox
from tkinter.ttk import Progressbar


class AdjustApp:
    def __init__(self, master, write_command, return_to_main):
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main
        self.is_active = True

        # Create a frame to hold the widgets
        self.frame = LabelFrame(master)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add Stop button to return to the main interface
        self.btn_back = Button(
            self.frame, text="Close", command=self.wrapper_return_to_main
        )
        self.btn_back.pack(pady=10)

        # Create a LabelFrame for Voltage
        self.voltage_frame = LabelFrame(self.frame, text="ADC Tunnel")
        self.voltage_frame.pack(fill="x", padx=10, pady=10)
        self.voltage_frame.config(height=150)  # Adjust the height of the voltage frame

        # Add a label inside the Voltage frame
        self.voltage_label = Label(self.voltage_frame, text="0", font=("Arial", 20))
        self.voltage_label.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Add a label for digits below the voltage_label
        self.digits_label = Label(
            self.voltage_frame, text="Digits: 0", font=("Arial", 10)
        )
        self.digits_label.grid(row=1, column=0, padx=10, pady=10, sticky="n")

        # Add a Progressbar inside the Voltage frame
        self.voltage_progressbar = Progressbar(
            self.voltage_frame,
            style="Thin.Horizontal.TProgressbar",
            orient=VERTICAL,
            length=150,
            mode="determinate",
            maximum=0x7FFF,
        )
        self.voltage_progressbar.grid(
            row=0, column=1, rowspan=2, padx=10, pady=10, sticky="ns"
        )

        # Configure grid columns to center the labels and progress bar
        self.voltage_frame.grid_columnconfigure(0, weight=1)
        self.voltage_frame.grid_columnconfigure(1, weight=0)

        # Create a LabelFrame for Tip
        self.tip_frame = LabelFrame(self.frame, text="")
        self.tip_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.tip_frame.config(height=400)  # Adjust the height of the tip frame

        # Create LabelFrames for Tip X, Tip Y, Tip Z and place them from left to right
        self.tip_x_frame = LabelFrame(self.tip_frame, text="DAC X")
        self.tip_x_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        self.tip_y_frame = LabelFrame(self.tip_frame, text="DAC Y")
        self.tip_y_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        self.tip_z_frame = LabelFrame(self.tip_frame, text="DAC Z")
        self.tip_z_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        # SLIDERS X Y Z
        slider_length = 300
        up = int("FFFF", 16)
        resolution = 100

        # SLIDER helper to reduce duplication
        def _create_slider(parent):
            """Create a vertical Scale + value Label inside `parent`.

            Returns (scale_widget, value_label).
            """

            scale = Scale(
                parent,
                from_=0,
                to=up,
                orient=VERTICAL,
                length=slider_length,
                showvalue=True,
                resolution=resolution,
            )
            scale.pack(pady=5)
            scale.bind("<ButtonRelease-1>", self.on_slider_xyz_button_release)

            lbl = Label(parent, text=scale.get(), width=10, font=("Arial", 15))
            lbl.pack(pady=5)
            return scale, lbl

        # TIP X
        self.slider_x, self.lb_x = _create_slider(self.tip_x_frame)

        # TIP Y
        self.slider_y, self.lb_y = _create_slider(self.tip_y_frame)

        # TIP Z
        self.slider_z, self.lb_z = _create_slider(self.tip_z_frame)

        self.send_adjust_to_esp()

    def send_adjust_to_esp(self):
        try:
            if callable(self.write_command):
                self.write_command("ADJUST")
            else:
                print("AdjustApp: write_command not set, skipping ADJUST")
        except Exception as e:
            print(f"AdjustApp: error sending ADJUST: {e}")

    def wrapper_return_to_main(self):
        self.is_active = False
        # Unbind Escape if it was bound on toplevel
        try:
            toplevel = self.frame.winfo_toplevel()
            toplevel.unbind_all("<Escape>")
        except Exception:
            try:
                self.master.unbind_all("<Escape>")
            except Exception:
                pass
        self.return_to_main()

    def on_slider_xyz_button_release(self, event):
        """Handles slider button release to update tip positions"""
        newx = self.slider_x.get()
        newy = self.slider_y.get()
        newz = self.slider_z.get()

        sendstring = f"TIP,{newx},{newy},{newz}"
        try:
            self.write_command(sendstring)
        except Exception as e:
            error_message = f"ERROR in set_tip_xxz {e}"
            messagebox.showerror("Error", error_message)

    def update_data(self, message):
        """Updates the Adjust interface with new data"""

        data = message.split(",")
        if data[0] == "ADJUST":
            # Update voltage label
            vf = float(data[1])
            v = format(vf, ".3f")
            self.voltage_label.config(text=v)

            # Update digits label
            nA = data[2].rjust(5, " ")
            digits = data[3].rjust(5, " ")
            display_str = f"{nA} [nA] {digits} [digits]"
            self.digits_label.config(text=display_str)

            # Update voltage progress bar
            self.voltage_progressbar["value"] = float(data[3])

    def destroy(self):
        """Destroys all widgets created by AdjustApp"""
        self.is_active = False
        self.voltage_frame.destroy()
        self.tip_frame.destroy()
