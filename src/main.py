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
    PhotoImage
)
from tkinter import ttk
import usb_connection
import measure
from adjust import AdjustApp
from parameter import ParameterApp
import serial.tools.list_ports
import settings
import os

# Define the global STATUS variable
STATUS = "INIT"


class EspApiClient:
    def __init__(self, master):
        self.master = master
        self.master.title("500 EUR RTM - Connecting ...")
        self.master.geometry("800x600")

        # Set the window icon
        icon_path = os.path.join(
            os.path.dirname(__file__), "../assets/icons/stm_symbol.ico"
        )
        self.master.iconbitmap(icon_path)

        self.setup_gui_interface()

        # Initialize the USB connection handler
        self.usb_conn = usb_connection.USBConnection(
            update_terminal_callback=self.update_terminal,
            dispatcher_callback=self.dispatch_received_data,
        )

        # Attempt to establish a USB connection
        if not self.connect():
            self.select_port()

        # Initialize the AdjustApp instance
        self.adjust_app = None

        # Initialize the ParameterApp instance
        self.parameter_app = None

        self.measure_app = None

    def setup_gui_interface(self):
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
        self.menu_bar.add_command(label="Measure", command=self.open_measure)

        # Create an Adjust menu
        self.menu_bar.add_command(label="Adjust", command=self.open_adjust)

        # Create a Parameter menu
        self.menu_bar.add_command(label="Parameter", command=self.open_parameter)

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

        # Create a frame to hold the content of the apps
        self.app_frame = Frame(self.master)
        self.app_frame.pack(side="right", fill="both", expand=True)

    def select_port(self):
        # Create a dialog to select the COM port
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
        # Refresh the list of available COM ports
        self.port_listbox.delete(0, END)
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            self.port_listbox.insert(END, port.device)

    def set_selected_port(self):
        # Set the selected COM port
        selected_index = self.port_listbox.curselection()
        if selected_index:
            selected_port = self.port_listbox.get(selected_index)
            settings.USB_PORT = selected_port
            self.port_dialog.destroy()
            self.connect()
        else:
            messagebox.showerror("Port Selection Error", "No port selected.")

    def connect(self):
        # Establish a connection to the selected COM port
        global STATUS
        try:
            self.usb_conn.port = settings.USB_PORT
            if self.usb_conn.establish_connection():
                self.usb_conn.check_esp_idle_response()
                # Update the window title with the COM port
                self.master.title(
                    f"500 EUR RTM - {self.usb_conn.port} {self.usb_conn.baudrate} baud"
                )

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

        if self.terminal and self.terminal.winfo_exists():
            self.terminal.insert(END, message + "\n")
            self.terminal.see(END)

    def dispatch_received_data(self, message):
        # Dispatch received data based on the current status
        global STATUS
        ms = message.split(",")
        messagetype = ms[0]

        if messagetype == "ADJUST":
            self.update_terminal(message)
            if self.adjust_app and self.adjust_app.is_active:
                self.adjust_app.update_data(message)
        elif messagetype == "PARAMETER":
            self.update_terminal(message)
            if self.parameter_app:
                self.parameter_app.update_data(message)
        elif messagetype == "DATA":
            try:
                if len(ms) == 2 and ms[1] == "DONE":
                    self.measure_app.redraw_plot()
                    self.update_terminal("Measurement complete.")

                # self.return_to_main()
                if len(ms) == 4:
                    self.measure_app.update_data(message)

                # Plot next set of data
                if ms[1]=="0":
                    self.update_terminal(f"Processing Y {ms[2]}")
            except Exception as e:
                self.update_terminal(f"Error measure: {message}, \nError: {e}")

    def open_measure(self):
        # Open the MEASURE interface
        global STATUS
        STATUS = "MEASURE"
        # Clear the app frame
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        # Open the MEASURE interface in the app frame
        self.measure_app=measure.MeasureApp(
            master=self.app_frame,
            write_command=self.usb_conn.write_command,
            return_to_main=self.return_to_main)

    def open_adjust(self):
        # Open the ADJUST interface
        global STATUS
        STATUS = "ADJUST"

        # Clear the app frame
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        # Open the ADJUST interface in the app frame
        self.adjust_app = AdjustApp(
            master=self.app_frame,
            write_command=self.usb_conn.write_command,
            return_to_main=self.return_to_main
        )

    def open_parameter(self):
        # Open the PARAMETER interface
        global STATUS
        STATUS = "PARAMETER"
        # self.usb_conn.write_command("PARAMETER,?")

        # Clear the app frame
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        # Open the PARAMETER interface in the app frame
        self.parameter_app = ParameterApp(
            self.app_frame, self.usb_conn.write_command, self.return_to_main
        )
        self.parameter_app.request_parameter()

    def return_to_main(self):
        # Restart esp
        # self.usb_conn.esp_restart()

        self.usb_conn.write_command("RESTART")
        # Clear the app frame
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        # Recreate the main interface
        self.create_main_interface()

    def create_main_interface(self):
        # Clear the existing interface
        for widget in self.master.winfo_children():
            widget.destroy()
        # Re-setup the interface without reinitializing the COM port
        self.setup_gui_interface()

    def open_settings(self):
        # Implement the settings window or dialog here
        messagebox.showinfo("Settings", "Settings window not implemented yet.")

    def on_closing(self):
        # Stop receiving data and close the application
        if self.usb_conn.esp_to_queue:
            self.usb_conn.esp_to_queue.stop_esp_to_queue()
        self.master.destroy()


if __name__ == "__main__":
    root = Tk()
    style = ttk.Style(root)
    style.theme_use("default")  # Use a simple theme
    style.configure("Thin.Horizontal.TProgressbar", thickness=10)  # Set the thickness

    esp_api_client = EspApiClient(root)
    root.protocol("WM_DELETE_WINDOW", esp_api_client.on_closing)
    root.mainloop()
