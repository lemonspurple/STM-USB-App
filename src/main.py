from tkinter import Tk, Frame, Button, Text, Scrollbar, END, Toplevel
import usb_connection
import measure
import adjust

class EspApiClient:
    def __init__(self, master):
        self.master = master
        self.master.title("500 EUR RTM - Connecting ...")

        # Create a frame to hold the terminal and scrollbar
        self.frame = Frame(self.master)
        self.frame.pack()

        # Create a text widget to act as a terminal
        self.terminal = Text(self.frame, height=15, width=50)
        self.terminal.pack(side='left', fill='both', expand=True)

        # Create a scrollbar for the terminal
        self.scrollbar = Scrollbar(self.frame, command=self.terminal.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.terminal['yscrollcommand'] = self.scrollbar.set

        # Create a button to establish USB connection
        self.connect_button = Button(self.master, text="Connect", command=self.connect)
        self.connect_button.pack()

        # Create a button to open the MEASURE interface, initially hidden
        self.measure_button = Button(self.master, text="MEASURE", command=self.open_measure)
        self.measure_button.pack_forget()

        # Create a button to open the ADJUST interface, initially hidden
        self.adjust_button = Button(self.master, text="ADJUST", command=self.open_adjust)
        self.adjust_button.pack_forget()

        # Initialize the USB connection handler
        self.usb_conn = usb_connection.USBConnection(self.update_terminal, self.dispatch_data)
        # Periodically process the queue
        self.master.after(100, self.process_queue)

    def connect(self):
        # Attempt to establish a USB connection
        if self.usb_conn.establish_connection():
            # Update the window title with the COM port
            self.master.title(f"500 EUR RTM - Connected to {self.usb_conn.port}")
            # Hide the connection GUI
            self.connect_button.pack_forget()
            # Show the MEASURE and ADJUST buttons
            self.measure_button.pack()
            self.adjust_button.pack()
        else:
            self.update_terminal("Failed to establish connection.")

    def update_terminal(self, message):
        # Update the terminal with a new message
        self.terminal.insert(END, message + '\n')
        self.terminal.see(END)

    def process_queue(self):
        self.usb_conn.process_queue()
        self.master.after(100, self.process_queue)

    def dispatch_data(self, message):
        # Dispatch data to the appropriate GUI
        if message.startswith("MEASURE"):
            # Send data to the MEASURE interface
            measure.MeasureWindow.update_data(message)
        elif message.startswith("ADJUST"):
            # Send data to the ADJUST interface
            adjust.AdjustWindow.update_data(message)
        else:
            self.update_terminal(message)

    def open_measure(self):
        # Open the MEASURE interface
        measure.MeasureWindow(Toplevel(self.master))

    def open_adjust(self):
        # Open the ADJUST interface
        adjust.AdjustWindow(Toplevel(self.master))

    def on_closing(self):
        # Stop receiving data
        if self.usb_conn.receiver:
            self.usb_conn.receiver.stop_receiving()
        # Close the application
        self.master.destroy()


if __name__ == "__main__":
    root = Tk()
    esp_api_client = EspApiClient(root)
    root.mainloop()