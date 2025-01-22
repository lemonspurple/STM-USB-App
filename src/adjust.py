from tkinter import Label, Button, LabelFrame, Scale, VERTICAL, messagebox
from tkinter.ttk import Progressbar
import time


class AdjustApp:

    def __init__(self, master, write_command, return_to_main):
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main
        self.is_active = True

        # Create a LabelFrame for Voltage
        self.voltage_frame = LabelFrame(master, text="ADC Tunnel")
        self.voltage_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.voltage_frame.config(height=250)

        # Add a label inside the Voltage frame
        self.voltage_label = Label(self.voltage_frame, text="0", font=("Arial", 20))
        self.voltage_label.pack(pady=10)

        # Add a label for digits below the voltage_label
        self.digits_label = Label(
            self.voltage_frame, text="Digits: 0", font=("Arial", 10)
        )
        self.digits_label.pack(pady=10)

        # Add a Progressbar inside the Voltage frame
        self.voltage_progressbar = Progressbar(
            self.voltage_frame,
            style="Thin.Horizontal.TProgressbar",
            orient=VERTICAL,
            length=200,
            mode="determinate",
            maximum=0x7FFF,
        )
        self.voltage_progressbar.pack(side="right", padx=10, pady=10)

        # Create a LabelFrame for Tip
        self.tip_frame = LabelFrame(master, text="")
        self.tip_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create LabelFrames for Tip X, Tip Y, Tip Z and place them from left to right
        self.tip_x_frame = LabelFrame(self.tip_frame, text="Tip X")
        self.tip_x_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        self.tip_y_frame = LabelFrame(self.tip_frame, text="Tip Y")
        self.tip_y_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        self.tip_z_frame = LabelFrame(self.tip_frame, text="Tip Z")
        self.tip_z_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        # SLIDERS X Y Z
        slider_length = 200
        up = int("FFFF", 16)
        resolution = 100

        # TIP X #########################
        self.slider_x = Scale(
            self.tip_x_frame,
            from_=0,
            to=up,
            orient=VERTICAL,
            length=slider_length,
            showvalue=True,
            resolution=resolution,
        )
        self.slider_x.pack(pady=5)

        # Bind the ButtonRelease-1 event to the on_slider_xyz_button_release function
        self.slider_x.bind("<ButtonRelease-1>", self.on_slider_xyz_button_release)

        self.lb_x = Label(
            self.tip_x_frame, text=self.slider_x.get(), width=10, font=("Arial", 15)
        )
        self.lb_x.pack(pady=5)

        # TIP Y #########################
        self.slider_y = Scale(
            self.tip_y_frame,
            from_=0,
            to=up,
            orient=VERTICAL,
            length=slider_length,
            showvalue=True,
            resolution=resolution,
        )
        self.slider_y.pack(pady=5)

        # Bind the ButtonRelease-1 event to the on_slider_xyz_button_release function
        self.slider_y.bind("<ButtonRelease-1>", self.on_slider_xyz_button_release)

        self.lb_y = Label(
            self.tip_y_frame, text=self.slider_y.get(), width=10, font=("Arial", 15)
        )
        self.lb_y.pack(pady=5)

        # TIP Z #########################
        self.slider_z = Scale(
            self.tip_z_frame,
            from_=0,
            to=up,
            orient=VERTICAL,
            length=slider_length,
            showvalue=True,
            resolution=resolution,
        )
        self.slider_z.pack(pady=5)

        # Bind the ButtonRelease-1 event to the on_slider_xyz_button_release function
        self.slider_z.bind("<ButtonRelease-1>", self.on_slider_xyz_button_release)

        self.lb_z = Label(
            self.tip_z_frame, text=self.slider_z.get(), width=10, font=("Arial", 15)
        )
        self.lb_z.pack(pady=5)

        # Add Back button to return to the main interface
        self.btn_back = Button(
            self.tip_frame, text="Back", command=self.wrapper_return_to_main
        )
        self.btn_back.pack(pady=10)

    def wrapper_return_to_main(self):
        self.is_active = False
        self.return_to_main()

    def on_slider_xyz_button_release(self, event):
        """Handles slider button release to update tip positions"""
        newx = self.slider_x.get()
        newy = self.slider_y.get()
        newz = self.slider_z.get()

        sendstring = f"TIP,{newx},{newy},{newz}\n"
        try:
            self.write_command(sendstring)
        except Exception as e:
            error_message = f"ERROR in set_tip_xxz {e}"
            messagebox.showerror("Error", error_message)

    def update_data(self, message):
        """Updates the Adjust interface with new data"""

        data = message.split(',')
        if data[0] == 'ADJUST':
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
            self.voltage_progressbar['value'] = float(data[3])

    def destroy(self):
        """Destroys all widgets created by AdjustApp"""
        self.is_active = False
        self.voltage_frame.destroy()
        self.tip_frame.destroy()
