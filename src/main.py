from tkinter import (
    Tk,
    Frame,
    Button,
    Text,
    Scrollbar,
    END,
    Toplevel,
    messagebox,
    Menu,
    Listbox,
    SINGLE,
)
import usb_connection
import measure
from adjust import AdjustApp
import threading
import serial.tools.list_ports
import settings

# Define the global STATUS variable
STATUS = "INIT"


class EspApiClient:
    def __init__(self, master):
        self.master = master
        self.master.title("500 EUR RTM - Connecting ...")
        self.master.geometry("800x600")

        # Create a menu bar
        self.menu_bar = Menu(self.master)
        self.master.config(menu=self.menu_bar)

        # Create a File menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Settings", command=self.open_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_closing)

        # Create a Measure menu
        self.measure_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Measure", menu=self.measure_menu)
        self.measure_menu.add_command(label="Open Measure", command=self.open_measure)

        # Create an Adjust menu
        self.adjust_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Adjust", menu=self.adjust_menu)
        self.adjust_menu.add_command(label="Open Adjust", command=self.open_adjust)

        # Create a frame to hold the terminal and scrollbar
        self.terminal_frame = Frame(self.master)
        self.terminal_frame.pack(side="left", fill="y")

        # Create a text widget to act as a terminal
        self.terminal = Text(self.terminal_frame, height=15, width=30)
        self.terminal.pack(side="left", fill="both", expand=False)

        # Create a scrollbar for the terminal
        self.scrollbar = Scrollbar(self.terminal_frame, command=self.terminal.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.terminal["yscrollcommand"] = self.scrollbar.set

        # Create a button to open the MEASURE interface, initially hidden
        self.measure_button = Button(
            self.master, text="MEASURE", command=self.open_measure
        )
        self.measure_button.pack_forget()

        # Create a frame to hold the content of the apps
        self.app_frame = Frame(self.master)
        self.app_frame.pack(side="right", fill="both", expand=True)

        # Initialize the USB connection handler
        self.usb_conn = usb_connection.USBConnection(
            self.update_terminal, self.dispatch_data
        )

        # Attempt to establish a USB connection
        if not self.connect():
            self.select_port()

    def select_port(self):
        self.port_dialog = Toplevel(self.master)
        self.port_dialog.title("Select Port")

        # Center the dialog on the screen
        self.port_dialog.geometry(
            "300x300+{}+{}".format(
                int(self.master.winfo_screenwidth() / 2 - 150),
                int(self.master.winfo_screenheight() / 2 - 150),
            )
        )

        self.port_listbox = Listbox(self.port_dialog, selectmode=SINGLE)
        self.port_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_ports()

        # Create a frame to hold the buttons
        button_frame = Frame(self.port_dialog)
        button_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.select_button = Button(
            button_frame, text="Select", command=self.set_selected_port
        )
        self.select_button.pack(side="left", padx=10, pady=10)

        self.refresh_button = Button(
            button_frame, text="Refresh", command=self.refresh_ports
        )
        self.refresh_button.pack(side="right", padx=10, pady=10)

        self.port_dialog.transient(self.master)
        self.port_dialog.grab_set()
        self.master.wait_window(self.port_dialog)

    def refresh_ports(self):
        self.port_listbox.delete(0, END)
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            self.port_listbox.insert(END, port.device)

    def set_selected_port(self):
        selected_index = self.port_listbox.curselection()
        if selected_index:
            selected_port = self.port_listbox.get(selected_index)
            settings.USB_PORT = selected_port
            self.port_dialog.destroy()
            self.connect()
        else:
            messagebox.showerror("Port Selection Error", "No port selected.")

    def connect(self):
        global STATUS
        try:
            self.usb_conn.port = settings.USB_PORT
            if self.usb_conn.establish_connection():
                # Update the window title with the COM port
                self.master.title(f"500 EUR RTM - Connected to {self.usb_conn.port}")
                # Show the MEASURE and ADJUST buttons
                self.measure_button.pack()

                STATUS = "IDLE"
                return True
            else:
                return False
        except Exception as e:
            self.update_terminal(f"Error establishing connection: {e}")
            messagebox.showerror(
                "Connection Error", f"Error establishing connection: {e}"
            )

    def update_terminal(self, message):
        # Update the terminal with a new message
        if self.terminal:
            self.terminal.insert(END, message + "\n")
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
        STATUS = "MEASURE"
        # Clear the app frame
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        # Open the MEASURE interface in the app frame
        measure.MeasureApp(self.app_frame)

    def open_adjust(self):
        self.measure_button.pack_forget()
        global STATUS
        STATUS = "ADJUST"
        # Clear the app frame
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        # Open the ADJUST interface in the app frame
        AdjustApp(self.app_frame)

    def open_settings(self):
        # Implement the settings window or dialog here
        messagebox.showinfo("Settings", "Settings window not implemented yet.")

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
