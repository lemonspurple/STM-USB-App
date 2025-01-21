from tkinter import Tk, Frame, Button, Text, Scrollbar, END, Toplevel, messagebox
import usb_connection
import measure
from adjust import AdjustApp
import threading

# Define the global STATUS variable
STATUS = 'INIT'

class EspApiClient:
    def __init__(self, master):
        self.master = master
        self.master.title("500 EUR RTM - Connecting ...")
        self.master.geometry("800x600")

        # Create a frame to hold the terminal and scrollbar
        self.terminal_frame = Frame(self.master)
        self.terminal_frame.pack(side='left', fill='y')

        # Create a text widget to act as a terminal
        self.terminal = Text(self.terminal_frame, height=15, width=30)
        self.terminal.pack(side='left', fill='both', expand=False)

        # Create a scrollbar for the terminal
        self.scrollbar = Scrollbar(self.terminal_frame, command=self.terminal.yview)
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

        # Create a frame to hold the content of the apps
        self.app_frame = Frame(self.master)
        self.app_frame.pack(side='right', fill='both', expand=True)

        # Initialize the USB connection handler
        self.usb_conn = usb_connection.USBConnection(self.update_terminal, self.dispatch_data)

        # Attempt to establish a USB connection
        self.connect()

    def connect(self):
        global STATUS
        try:
            if self.usb_conn.establish_connection():
                # Update the window title with the COM port
                self.master.title(f"500 EUR RTM - Connected to {self.usb_conn.port}")
                # Hide the connection GUI
                self.connect_button.pack_forget()
                # Show the MEASURE and ADJUST buttons
                self.measure_button.pack()
                self.adjust_button.pack()
                STATUS = "IDLE"
            else:
                messagebox.showerror("Connection Error", "Failed to establish connection.")
                
                self.master.after(0, self.master.destroy)
        except Exception as e:
            self.update_terminal(f"Error establishing connection: {e}")
            self.master.after(0, self.master.destroy)

    def update_terminal(self, message):
        # Update the terminal with a new message
        if self.terminal:
            self.terminal.insert(END, message + '\n')
            self.terminal.see(END)

    def read_queue_loop(self):
        self.usb_conn.read_queue()
        self.master.after(100, self.read_queue_loop)

    def dispatch_data(self, message):
        # Dispatch data to the appropriate GUI
        if message.startswith("MEASURE"):
            # Send data to the MEASURE interface
            measure.MeasureWindow.update_data(message)
        elif message.startswith("ADJUST"):
            # Send data to the ADJUST interface
            AdjustApp.update_data(message)
        else:
            self.update_terminal(message)

    def open_measure(self):
        global STATUS
        STATUS = 'MEASURE'
        # Clear the app frame
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        # Open the MEASURE interface in the app frame
        measure.MeasureWindow(self.app_frame)

    def open_adjust(self):
        global STATUS
        STATUS = 'ADJUST'
        # Clear the app frame
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        # Open the ADJUST interface in the app frame
        AdjustApp(self.app_frame)

    def on_closing(self):
        # Stop receiving data
        if self.usb_conn.esp_to_queue:
            self.usb_conn.esp_to_queue.stop_esp_to_queue()
        # Close the application
        self.master.destroy()


if __name__ == "__main__":
    root = Tk()
    esp_api_client = EspApiClient(root)
    root.protocol("WM_DELETE_WINDOW", esp_api_client.on_closing)
    root.mainloop()
