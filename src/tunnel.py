from tkinter import Frame, Button
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TunnelApp:
    def __init__(self, master, write_command, return_to_main):
        # Initialize TunnelApp with callbacks and settings
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

        # Initialize the plot
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        # Set initial plot limits
        self.ax.set_xlim(0, 100)  # Initial limit for x-axis (counter)
        self.ax.set_ylim(0, 0x7FFF)  # Initial limit for y-axis (data values)
        self.ax.set_xlabel("Counter")
        self.ax.set_ylabel("Value")
        self.ax.set_title("Data Values over Counter")
        self.canvas.draw()

        # Initialize data lists
        self.counter = 0
        self.adc_data = []
        self.z_data = []
        self.colors = []

        # Start the measurement process
        self.write_command("TUNNEL")

    def wrapper_return_to_main(self):
        # Set is_active to False and return to the main interface
        self.is_active = False
        self.return_to_main()

    def update_data(self, message):
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

        self.counter += 1
        self.adc_data.append(adc)
        self.z_data.append(z)
        self.colors.append("red" if flag == 0 else "green")

       
        
        if self.counter % 100 == 0:
            self.redraw_plot()

    def redraw_plot(self):
        # Clear the plot and redraw
        self.ax.clear()
        self.ax.scatter(
            range(len(self.adc_data)),
            self.adc_data,
            c=self.colors,
            marker="o",
            label="ADC",
        )
        self.ax.scatter(
            range(len(self.z_data)), self.z_data, c=self.colors, marker="x", label="Z"
        )
        self.ax.set_xlim(
            0, max(100, len(self.adc_data))
        )  # Adjust x-axis limit based on data length
        self.ax.set_xlim(0, 5000)
        self.ax.set_ylim(0, 0x7FFF)  # Adjust y-axis limit if needed
        self.ax.set_xlabel("Counter")
        self.ax.set_ylabel("Value")
        self.ax.set_title("Data Values over Counter")
        self.ax.legend()
        self.canvas.draw()
