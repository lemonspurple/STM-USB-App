import serial.tools.list_ports
import config_utils
from tkinter import END, Toplevel, Listbox, SINGLE, Button, Frame, messagebox

def refresh_ports(port_listbox):
    # Refresh the list of available COM ports
    port_listbox.delete(0, END)
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        port_listbox.insert(END, port.device)

def set_selected_port(port_listbox, port_dialog):
    # Set the selected COM port
    selected_index = port_listbox.curselection()
    if selected_index:
        selected_port = port_listbox.get(selected_index)
        config_utils.set_config("USB", "port", selected_port)
        port_dialog.destroy()
    else:
        messagebox.showerror("Port Selection Error", "No port selected.")


def is_com_port_available(port):
    # Check if the specified COM port is available
    available_ports = [p.device for p in serial.tools.list_ports.comports()]
    return port in available_ports


def select_port(master):
    # Create a dialog to select the COM port
    port_dialog = Toplevel(master)
    port_dialog.title("Select Port")

    # Center the dialog on the screen
    port_dialog.geometry(
        "300x300+{}+{}".format(
            int(master.winfo_screenwidth() / 2 - 150),
            int(master.winfo_screenheight() / 2 - 150),
        )
    )

    port_listbox = Listbox(port_dialog, selectmode=SINGLE)
    port_listbox.pack(fill="both", expand=True, padx=10, pady=10)

    refresh_ports(port_listbox)

    # Create a frame to hold the buttons
    button_frame = Frame(port_dialog)
    button_frame.pack(fill="both", expand=True, padx=10, pady=10)

    select_button = Button(
        button_frame, text="Connect", command=lambda: set_selected_port(port_listbox, port_dialog)
    )
    select_button.pack(side="left", padx=10, pady=10)

    refresh_button = Button(
        button_frame, text="Refresh", command=lambda: refresh_ports(port_listbox)
    )
    refresh_button.pack(side="right", padx=10, pady=10)

    port_dialog.transient(master)
    port_dialog.grab_set()
    master.wait_window(port_dialog)
