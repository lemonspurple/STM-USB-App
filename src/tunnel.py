from tkinter import Frame, Button
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation


class TunnelApp:
    def __init__(self, master, write_command, return_to_main):
        # Initialize MeasureApp with callbacks and settings
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main
        self.is_active = True

        # Create a frame to hold the widgets
        self.frame = Frame(master)
        self.frame.pack()

        # Create a Back button to return to the main interface
        self.btn_back = Button(
            self.frame, text="Stop", command=self.wrapper_return_to_main
        )
        self.btn_back.pack(pady=10)

        # Start the measurement process
        self.write_command("TUNNEL")

    def wrapper_return_to_main(self):
        # Set is_active to False and return to the main interface
        self.is_active = False
        self.return_to_main()

    def update_data(self, message):

        print(f"Updating data with message: {message}")