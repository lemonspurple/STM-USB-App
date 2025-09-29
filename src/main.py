import time
import threading
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
import config_utils
import os
import sys
import com_port_utils  # Import the com_port_utils module
import msvcrt
import atexit


# Define the global STATUS variable
STATUS = "INIT"

lock_handle = None
running = True


def prevent_multiple_instances():
    global lock_handle
    lock_file = (
        os.path.join(os.path.dirname(sys.executable), "app.lock")
        if hasattr(sys, "_MEIPASS")
        else "app.lock"
    )
    lock_handle = open(lock_file, "w")
    try:
        msvcrt.locking(lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        print("Another instance of the application is already running.")
        sys.exit(1)

    # Register a cleanup function to delete the lock file on exit
    atexit.register(delete_lock_file, lock_file)


def delete_lock_file(lock_file):
    global lock_handle
    try:
        if lock_handle:
            msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 1)  # Unlock the file
            lock_handle.close()
            lock_handle = None  # Set to None after closing
        if os.path.exists(lock_file):
            os.remove(lock_file)  # Delete the lock file
        print("Lock file deleted.")
    except Exception as e:
        print(f"Error deleting lock file: {e}")


def cleanup_tasks():
    global running, lock_handle
    running = False  # Signal the thread to stop
    print("Cleaning up tasks...")

    if lock_handle:  # Only unlock and close if not already handled
        msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
        lock_handle.close()
        lock_handle = None  # Set to None after closing
    print("FOO All tasks closed.")
    # esp_api_client.close_usb_connection()  # Uncommented to close USB connection


def global_on_close():
    print("on_close: Function triggered")
    print("FOO send STOP #########################")
    try:
        esp_api_client.usb_conn.write_command("STOP")
    except Exception as e:
        print(f"Error sending STOP command: {e}")
    cleanup_tasks()
    root.destroy()


class MasterGui:
    def __init__(self, master):
        self.master = master
        self.master.title("500 EUR RTM - Connecting ...")
        self.master.geometry("900x600")

        # Use sys._MEIPASS to find the file in all environments
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        # Set the window icon

        icon_path = os.path.join(base_path, "assets", "icons", "stm_symbol.ico")

        self.master.iconbitmap(icon_path)

        self.setup_gui_interface()
        # Initialize the USB connection handler
        self.initialize_usb_connection()

        # Initialize the idle_received attribute
        self.idle_received = False

        # Initialize the AdjustApp instance
        self.adjust_app = None

        # Initialize the ParameterApp instance
        self.parameter_app = None

        self.measure_app = None
        self.target_adc = 0
        self.tolerance_adc = 0

    def initialize_usb_connection(self):
        # Initialize the USB connection handler
        self.usb_conn = usb_connection.USBConnection(
            update_terminal_callback=self.update_terminal,
            dispatcher_callback=self.dispatch_received_data,
        )

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
        self.measure_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Measure", menu=self.measure_menu)
        self.measure_menu.add_command(label="Measure", command=self.open_measure)

        # Create a Parameter menu
        self.menu_bar.add_command(label="Parameter", command=self.open_parameter)

        # Create a Tools menu
        self.tools_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=self.tools_menu)
        self.tools_menu.add_command(label="DAC/ADC", command=self.open_adjust)
        self.tools_menu.add_command(label="Sinus", command=self.open_sinus)
        self.tools_menu.add_command(label="Tunnel", command=self.open_tunnel)
        self.tools_menu.add_separator()

        self.tools_menu.add_command(
            label="Tunnel Simulation", command=self.open_tunnel_simulate
        )
        self.tools_menu.add_command(
            label="Measure Simulation", command=self.open_measure_simulate
        )
       
        self.tools_menu.add_command(
            label="Info Simulation", command=self.show_simulation_info
        )

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

    def connect(self):
        # Establish a connection to the selected COM port
        global STATUS

        self.usb_conn.port = config_utils.get_config("USB", "port")

        self.update_terminal(f"Try to connect {self.usb_conn.port}...")

        if not com_port_utils.is_com_port_available(self.usb_conn.port):
            self.update_terminal(f"COM port {self.usb_conn.port} is not available")
            return False
        if not self.usb_conn.establish_connection():
            self.update_terminal(f"COM port {self.usb_conn.port} cannot connect")
            return False

        self.usb_conn.start_receiving()
        try:
            self.usb_conn.write_command("STOP")
        except Exception as e:
            self.update_terminal(f"Error sending STOP command")
            return False
        self.idle_received = False  # Reset idle_received before waiting
        start_time = time.time()
        while not self.idle_received:
            self.master.update()
            time.sleep(0.1)
            if time.time() - start_time > 1:
                return False
        time.sleep(0.1)
        STATUS = "IDLE"
        return True

    def try_to_connect(self):
        # Try to establish a connection and select port if it fails
        self.update_terminal(
            f"FOO Config file path: {config_utils.config_file}"
        )  # Show config.ini path
        if os.path.exists(config_utils.config_file):
            self.update_terminal("Config file exists.")
        else:
            self.update_terminal("Config file does not exist.")

        result = self.connect()
        while not result:
            com_port_utils.select_port(self.master)
            if config_utils.get_config("USB", "port") == "None":
                self.master.destroy()
                return
            result = self.connect()

        # Update the window title with the COM port
        self.master.title(
            f"500 EUR RTM - {self.usb_conn.port} {self.usb_conn.baudrate} baud"
        )

        self.usb_conn.write_command("PARAMETER,?")

    def update_terminal(self, message):
        # Update the terminal with a new message
        if (
            self.master.winfo_exists()
            and self.terminal
            and self.terminal.winfo_exists()
        ):
            self.terminal.insert(END, message + "\n")
            self.terminal.see(END)
            self.master.update_idletasks()  # Force update the terminal

    def dispatch_received_data(self, message):
        # Dispatch received data based on the current status
        global STATUS
        messages = message.split("\n")
        for msg in messages:
            ms = msg.split(",")
            messagetype = ms[0]
            if messagetype == "IDLE":
                self.idle_received = True
            if messagetype == "ADJUST":
                self.update_terminal(msg)
                if self.adjust_app and self.adjust_app.is_active:
                    self.adjust_app.update_data(msg)
            elif messagetype == "PARAMETER":
                self.update_terminal(msg)
                if ms[1] == "targetNa":
                    self.target_adc = self.calculate_adc_value(ms[2])
                if ms[1] == "toleranceNa":
                    self.tolerance_adc = self.calculate_adc_value(ms[2])
                if self.parameter_app:
                    self.parameter_app.update_data(msg)
            elif messagetype == "TUNNEL":

                adc_value = int(ms[2])
                if (
                    adc_value > 0x7FFF
                ):  # If greater than the max positive value for int16
                    adc_value -= 0x10000  # Convert to signed value
                ms[2] = str(adc_value)
                msg = ",".join(ms)

                self.update_terminal(msg)
                if self.tunnel_app:
                    self.tunnel_app.update_data(msg)
            elif messagetype == "FIND":
                self.update_terminal(msg)
            elif messagetype == "DATA":
                try:
                    if len(ms) == 2 and ms[1] == "DONE":
                        self.measure_app.redraw_plot()
                        self.update_terminal("Measurement complete.")

                    # self.return_to_main()
                    if len(ms) == 4:
                        self.measure_app.update_data(msg)

                    # Plot next set of data
                    if ms[1] == "0":
                        self.update_terminal(f"Processing Y {ms[2]}")
                except Exception as e:
                    self.update_terminal(f"Error measure: {msg}, \nError: {e}")

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
            simulate=False
        )
        self.disable_menu()

    def open_measure_simulate(self):
        # Open the MEASURE SIMULATE interface
        global STATUS
        STATUS = "MEASURE_SIMULATE"
        # Clear the app frame
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        # Open the MEASURE interface in the app frame
        self.measure_app = measure.MeasureApp(
            master=self.app_frame,
            write_command=self.usb_conn.write_command,
            return_to_main=self.return_to_main,
            simulate=True
        )
        self.disable_menu()

    def open_tunnel(self):
        # self.usb_conn.write_command("PARAMETER,?")
        global STATUS
        STATUS = "TUNNEL"

        for widget in self.app_frame.winfo_children():
            widget.destroy()

        self.tunnel_app = TunnelApp(
            master=self.app_frame,
            write_command=self.usb_conn.write_command,
            return_to_main=self.return_to_main,
            target_adc=self.target_adc,
            tolerance_adc=self.tolerance_adc,
            simulate=False
        )
        self.disable_menu()

    def open_tunnel_simulate(self):
        # Open the TUNNEL SIMULATE interface
        global STATUS
        STATUS = "TUNNEL_SIMULATE"

        for widget in self.app_frame.winfo_children():
            widget.destroy()

        self.tunnel_app = TunnelApp(
            master=self.app_frame,
            write_command=self.usb_conn.write_command,
            return_to_main=self.return_to_main,
            target_adc=self.target_adc,
            tolerance_adc=self.tolerance_adc,
            simulate=True,
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

    def show_simulation_info(self):
        # Show information about simulation mode
        messagebox.showinfo(
            "Info Simulation",
            "Simulation means: There is a connection between Ouput 'DAC_Z' and Tunnel Input 'TUN'",
        )

    def on_closing(self):
        try:
            self.usb_conn.write_command("STOP")
        except:
            pass
        finally:
            self.close_usb_connection()
            self.master.destroy()

    def close_usb_connection(self):
        # Close the USB connection to free the COM port
        try:
            self.usb_conn.close_connection()
        except Exception as e:
            self.update_terminal(f"Error closing USB connection: {e}")

    def calculate_adc_value(self, nA):
        # Convert nA to float
        try:
            nA = float(nA)
        except ValueError:
            self.update_terminal(f"Invalid nA value: {nA}")
            return 0
        # Calculate adcValue using the formula
        adc_voltage_divider = float(
            config_utils.get_config("ADC_TO_NA", "adc_voltage_divider")
        )  # Use the utility function
        adc_value_max = float(
            config_utils.get_config("ADC_TO_NA", "adc_value_max")
        )  # Use the utility function
        adc_voltage_max = float(
            config_utils.get_config("ADC_TO_NA", "adc_voltage_max")
        )  # Use the utility function

        adc_value = (nA / adc_voltage_divider) * (adc_value_max / adc_voltage_max)
        adc_value = int(adc_value)  # Convert to integer
        return adc_value


if __name__ == "__main__":
    prevent_multiple_instances()

    root = Tk()
    style = ttk.Style(root)
    style.theme_use("default")  # Use a simple theme
    style.configure("Thin.Horizontal.TProgressbar", thickness=10)  # Set the thickness

    esp_api_client = MasterGui(root)

    print("Binding WM_DELETE_WINDOW to on_close")
    root.protocol("WM_DELETE_WINDOW", global_on_close)
    root.after(100, esp_api_client.try_to_connect)

    print("Program is running...")
    root.mainloop()
    print("Program exited root.mainloop()")
