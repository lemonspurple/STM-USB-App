import tkinter as tk
from tkinter import Frame, Button


class SinusApp:
    def __init__(self, master, write_command, return_to_main):
        # Initialize Sinus with callbacks and settings
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main
        self.is_active = True

        # Create a frame to hold the widgets
        self.frame = Frame(master)
        self.frame.pack()

        # Create a label to display the sinus signal information
        self.label = tk.Label(self.frame, text="Sinus signal at ADC X, Y, Z")
        self.label.pack(pady=20)

        # Create a Stop button to return to the main interface
        self.btn_stop = Button(
            self.frame, text="Stop", command=self.wrapper_return_to_main
        )
        self.btn_stop.pack(pady=10)

    def wrapper_return_to_main(self):
        # Wrapper function to handle returning to the main interface
        self.is_active = False
        self.return_to_main()

    def request_sinus(self):
        self.write_command("SINUS")
