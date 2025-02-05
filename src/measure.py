from tkinter import Frame, Button
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

class MeasureApp:
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
        self.btn_back = Button(self.frame, text="Stop", command=self.wrapper_return_to_main)
        self.btn_back.pack(pady=10)

        # Create a Reset Rotation button to reset the 3D plot rotation
        self.btn_reset_rotation = Button(self.frame, text="Reset Rotation", command=self.reset_rotation)
        self.btn_reset_rotation.pack(pady=10)
        self.btn_reset_rotation.pack_forget()  # Initially hide the Reset Rotation button

        # Initialize the 3D plot
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.x_data = []
        self.y_data = []
        self.z_data = []

        # Store the initial rotation state
        self.initial_elev = self.ax.elev
        self.initial_azim = self.ax.azim

        # Embed the plot in a Tkinter canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.canvas.mpl_connect('motion_notify_event', self.on_plot_hover)  # Connect the hover event
        self.redraw_plot()

        # Start the measurement process
        self.write_command("MEASURE")

    def wrapper_return_to_main(self):
        # Set is_active to False and return to the main interface
        self.is_active = False
        self.return_to_main()

    def update_data(self, message):
        # Update the Parameter interface with new data
        data = message.split(",")
        try:
            x, y, z = int(data[1]), int(data[2]), int(data[3])
        except Exception as e:
            print(f"Error: {e}, \n{message}")
            return False

        self.x_data.append(x)
        self.y_data.append(y)
        self.z_data.append(z)

        if x == 0:
            self.redraw_plot()

    def redraw_plot(self):
        # Clear the plot and redraw
        self.ax.clear()
        self.ax.set_xlim(0, 200)
        self.ax.set_ylim(0, 200)
        self.ax.set_zlim(0, 0xFFFF)
        self.ax.plot(self.x_data, self.y_data, self.z_data)
        self.ax.set_xlabel('X')  
        self.ax.set_ylabel('Y')  
        self.ax.set_zlabel('Z')
        self.canvas.draw()

    def reset_rotation(self):
        # Reset the rotation of the 3D plot to its initial state
        self.ax.view_init(elev=self.initial_elev, azim=self.initial_azim)  # Reset to initial elevation and azimuthal angles
        self.canvas.draw()
        self.btn_reset_rotation.pack_forget()  # Hide the Reset Rotation button after resetting

    def on_plot_hover(self, event):
        # Show the Reset Rotation button only if the plot has been rotated
        if self.ax.elev != self.initial_elev or self.ax.azim != self.initial_azim:
            self.btn_reset_rotation.pack(pady=10)

    def animate(self, i):
        # Animation function to update the plot
        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data, self.z_data)

    def show_plot(self):
        # Show the plot in a separate window
        ani = animation.FuncAnimation(self.fig, self.animate, interval=100)
        plt.show()
