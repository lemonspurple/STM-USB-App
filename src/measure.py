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
        self.btn_back = Button(self.frame, text="Back", command=self.wrapper_return_to_main)
        self.btn_back.pack(pady=10)

        # Initialize the 3D plot
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.x_data = []
        self.y_data = []
        self.z_data = []

        # Embed the plot in a Tkinter canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
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

        if x==0:
            self.redraw_plot()

    def redraw_plot(self):
        # Clear the plot and redraw
        self.ax.clear()
        self.ax.set_xlim(0, 200)
        self.ax.set_ylim(0, 200)
        self.ax.set_zlim(0, 0xFFFF)
        self.ax.plot(self.x_data, self.y_data, self.z_data)
        self.canvas.draw()

    def animate(self, i):
        # Animation function to update the plot
        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data, self.z_data)

    def show_plot(self):
        # Show the plot in a separate window
        ani = animation.FuncAnimation(self.fig, self.animate, interval=100)
        plt.show()
