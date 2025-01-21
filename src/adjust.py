from tkinter import Label, Button, LabelFrame, Scale, VERTICAL

class AdjustApp:
    def __init__(self, master):
        self.master = master
        
        # Create a LabelFrame for Voltage
        self.voltage_frame = LabelFrame(master, text="Voltage")
        self.voltage_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add a label inside the Voltage frame
        self.voltage_label = Label(self.voltage_frame, text="Voltage Settings")
        self.voltage_label.pack(pady=10)

        # Create a LabelFrame for Tip
        self.tip_frame = LabelFrame(master, text="Tip")
        self.tip_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create LabelFrames for Tip X, Tip Y, Tip Z and place them from left to right
        self.tip_x_frame = LabelFrame(self.tip_frame, text="Tip X")
        self.tip_x_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        self.tip_y_frame = LabelFrame(self.tip_frame, text="Tip Y")
        self.tip_y_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        self.tip_z_frame = LabelFrame(self.tip_frame, text="Tip Z")
        self.tip_z_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        # Add labels inside the Tip X, Tip Y, Tip Z frames
        self.tip_x_label = Label(self.tip_x_frame, text="Tip X Settings")
        self.tip_x_label.pack(pady=5)

        self.tip_y_label = Label(self.tip_y_frame, text="Tip Y Settings")
        self.tip_y_label.pack(pady=5)

        self.tip_z_label = Label(self.tip_z_frame, text="Tip Z Settings")
        self.tip_z_label.pack(pady=5)

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
            self.tip_x_frame, text="wait ...", width=10, font=("Arial", 15)
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
            self.tip_y_frame, text="wait ...", width=10, font=("Arial", 15)
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
            self.tip_z_frame, text="wait ...", width=10, font=("Arial", 15)
        )
        self.lb_z.pack(pady=5)

    #     # Add an Adjust button
    #     self.adjust_button = Button(master, text="Adjust", command=self.perform_adjustment)
    #     self.adjust_button.pack(pady=10)

    #     # Add a status label
    #     self.status_label = Label(master, text="Status: Waiting for adjustment...")
    #     self.status_label.pack(pady=10)

    # def perform_adjustment(self):
    #     # Logic for performing adjustments goes here
    #     self.status_label.config(text="Adjustment performed!")

    def on_slider_xyz_button_release(self, event):
        # Logic for handling slider release event goes here
        if event.widget == self.slider_x:
            self.lb_x.config(text=f"Value: {self.slider_x.get()}")
        elif event.widget == self.slider_y:
            self.lb_y.config(text=f"Value: {self.slider_y.get()}")
        elif event.widget == self.slider_z:
            self.lb_z.config(text=f"Value: {self.slider_z.get()}")