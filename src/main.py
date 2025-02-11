import time
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
    PhotoImage,
)
from tkinter import ttk
from sinus import SinusApp
from tunnel import TunnelApp
import usb_connection
import measure
from adjust import AdjustApp
from parameter import ParameterApp
import serial.tools.list_ports
import configparser
import os

# Define the global STATUS variable
STATUS = "INIT"
# Create a ConfigParser object
config = configparser.ConfigParser()

# Define the path to the config file
config_file = os.path.join(os.path.dirname(__file__), "config.ini")

# Read the config file
config.read(config_file)


class MasterGui:
    def __init__(self, master):
        self.master = master
        self.master.title("500 EUR RTM - Connecting ...")
        self.master.geometry("900x600")

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
        self.target_adc = 0
        self.tolerance_adc = 0

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

        # Create a Parameter menu
        self.menu_bar.add_command(label="Parameter", command=self.open_parameter)

        # Create a Tools menu
        self.tools_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=self.tools_menu)
        self.tools_menu.add_command(label="DAC/ADC", command=self.open_adjust)
        self.tools_menu.add_command(label="Sinus", command=self.open_sinus)
        self.tools_menu.add_command(label="Tunnel", command=self.open_tunnel)

        # Create a frame to hold the terminal and scrollbar
        self.terminal_frame = Frame(self.master)
        self.terminal_frame.pack(side="left", fill="y")

        # Create a text widget to act as a terminal
        self.terminal = Text(self.terminal_frame, height=15, width=30)
        self.terminal.grid(row=0, column=0, sticky="nsew")

        # Create a scrollbar for the terminal
        self.scrollbar = Scrollbar(self.terminal_frame, command=self.terminal.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.terminal["yscrollcommand"] = self.scrollbar.set

        # Create a button to clear the terminal
        self.clear_terminal_button = Button(
            self.terminal_frame, text="Clear Terminal", command=self.clear_terminal
        )
        self.clear_terminal_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Configure grid weights to make the terminal expand
        self.terminal_frame.grid_rowconfigure(0, weight=1)
        self.terminal_frame.grid_columnconfigure(0, weight=1)

        # Create a frame to hold the content of the apps
        self.app_frame = Frame(self.master)
        self.app_frame.pack(side="right", fill="both", expand=True)

    def clear_terminal(self):
        # Clear the terminal content
        if self.terminal and self.terminal.winfo_exists():
            self.terminal.delete(1.0, END)

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
            config.set("USB", "PORT", selected_port)
            self.port_dialog.destroy()
            self.connect()
        else:
            messagebox.showerror("Port Selection Error", "No port selected.")

    def connect(self):
        # Establish a connection to the selected COM port
        global STATUS
        try:
            self.usb_conn.port = config.get("USB", "PORT")
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
            self.update_terminal(f"FooError establishing connection: {e}")
            messagebox.showerror(
                "Connection Error", f"Error establishing connection: {e}"
            )

    def update_terminal(self, message):
        # Update the terminal with a new message
        if (
            self.master.winfo_exists()
            and self.terminal
            and self.terminal.winfo_exists()
        ):
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
            if ms[1] == "targetNa":
                
                self.target_adc = self.calculate_adc_value(ms[2])
            if ms[1] == "toleranceNa":
                self.tolerance_adc = self.calculate_adc_value(ms[2])
            if self.parameter_app:
                self.parameter_app.update_data(message)
        elif messagetype == "TUNNEL":
            # self.update_terminal(message)
            if self.tunnel_app:
                self.tunnel_app.update_data(message)

        elif messagetype == "DATA":
            try:
                if len(ms) == 2 and ms[1] == "DONE":
                    self.measure_app.redraw_plot()
                    self.update_terminal("Measurement complete.")

                # self.return_to_main()
                if len(ms) == 4:
                    self.measure_app.update_data(message)

                # Plot next set of data
                if ms[1] == "0":
                    self.update_terminal(f"Processing Y {ms[2]}")
            except Exception as e:
                self.update_terminal(f"Error measure: {message}, \nError: {e}")

    def disable_menu(self):
        # Disable all menu points
        self.menu_bar.entryconfig("File", state="disabled")
        self.menu_bar.entryconfig("Measure", state="disabled")
        self.menu_bar.entryconfig("Parameter", state="disabled")
        self.menu_bar.entryconfig("Tools", state="disabled")

    def enable_menu(self):
        # Enable all menu points
        self.menu_bar.entryconfig("File", state="normal")
        self.menu_bar.entryconfig("Measure", state="normal")
        self.menu_bar.entryconfig("Parameter", state="normal")
        self.menu_bar.entryconfig("Tools", state="normal")

    def open_measure(self):
        # Open the MEASURE interface
        global STATUS
        STATUS = "MEASURE"
        # Clear the app frame
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        # Open the MEASURE interface in the app frame
        self.measure_app = measure.MeasureApp(
            master=self.app_frame,
            write_command=self.usb_conn.write_command,
            return_to_main=self.return_to_main,
        )
        self.disable_menu()

    def open_tunnel(self):
        #self.usb_conn.write_command("PARAMETER,?")
        global STATUS
        STATUS = "TUNNEL"

        for widget in self.app_frame.winfo_children():
            widget.destroy()

        self.tunnel_app = TunnelApp(
            master=self.app_frame,
            write_command=self.usb_conn.write_command,
            return_to_main=self.return_to_main,
            target_adc=self.target_adc,
            tolerance_adc=self.tolerance_adc
        )
        self.disable_menu()

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
            return_to_main=self.return_to_main,
        )
        self.disable_menu()

    def open_sinus(self):
        # Open the SINUS interface
        global STATUS
        STATUS = "SINUS"
        # Clear the app frame
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        # Open the SINUS interface in the app frame
        self.sinus_app = SinusApp(
            master=self.app_frame,
            write_command=self.usb_conn.write_command,
            return_to_main=self.return_to_main,
        )
        self.sinus_app.request_sinus()
        self.disable_menu()

    def open_parameter(self):
        # Open the PARAMETER interface
        global STATUS
        STATUS = "PARAMETER"

        # Clear the app frame
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        # Open the PARAMETER interface in the app frame
        self.parameter_app = ParameterApp(
            self.app_frame, self.usb_conn.write_command, self.return_to_main
        )
        self.parameter_app.request_parameter()
        self.disable_menu()

    def return_to_main(self):
        self.usb_conn.write_command("STOP")
        # Wait until all remaining data are shown in terminal

        # Clear the app frame
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        # Recreate the main interface

        self.create_main_interface()
        self.enable_menu()

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
        try:
            self.usb_conn.write_command("STOP")
        except:
            pass
        finally:
            self.master.destroy()

    def calculate_adc_value(self, nA):
        # Convert nA to float
        try:
            nA = float(nA)
        except ValueError:
            self.update_terminal(f"Invalid nA value: {nA}")
            return 0
        # Calculate adcValue using the formula
        adc_voltage_divider = float(config.get("PARAMETER", "ADC_VOLTAGE_DIVIDER"))
        adc_value_max = float(config.get("PARAMETER", "ADC_VALUE_MAX"))
        adc_voltage_max = float(config.get("PARAMETER", "ADC_VOLTAGE_MAX"))

        adc_value = (nA / adc_voltage_divider) * (adc_value_max / adc_voltage_max)
        adc_value = int(adc_value)  # Convert to integer
        return adc_value


if __name__ == "__main__":
    root = Tk()
    style = ttk.Style(root)
    style.theme_use("default")  # Use a simple theme
    style.configure("Thin.Horizontal.TProgressbar", thickness=10)  # Set the thickness

    esp_api_client = MasterGui(root)
    root.protocol("WM_DELETE_WINDOW", esp_api_client.on_closing)
    root.after(1000, esp_api_client.usb_conn.write_command, "PARAMETER,?")
    root.mainloop()
