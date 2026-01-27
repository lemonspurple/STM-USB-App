"""Small UI for sending a SINUS command and showing a brief label.

This module defines `SinusApp`, a minimal UI pane used to request
sinusoidal tuning from the device. The class keeps behavior simple and
isolated so it can be embedded in the main application window.
"""

from tkinter import Frame, Button, Label


class SinusApp:
    """UI pane for requesting a sinus measurement from the device.

    Parameters
    - master: parent widget
    - write_command: callable that sends a command string to the device
    - return_to_main: callable to switch back to main UI
    """

    def __init__(self, master, write_command, return_to_main):
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main
        self.is_active = True

        # main container
        self.frame = Frame(master)
        self.frame.pack(fill="both", expand=True)

        # button row
        self.button_frame = Frame(self.frame)
        self.button_frame.pack(fill="x", pady=10)

        self.btn_stop = Button(
            self.button_frame, text="Close", command=self.wrapper_return_to_main
        )
        self.btn_stop.pack(side="left", padx=10)

        # informational label
        self.label = Label(self.frame, text="Sinus signal at ADC X, Y, Z")
        self.label.pack(pady=20)

    def wrapper_return_to_main(self):
        # Wrapper function to handle returning to the main interface
        self.is_active = False
        # Unbind Escape handler if bound on toplevel
        try:
            toplevel = self.frame.winfo_toplevel()
            toplevel.unbind_all("<Escape>")
        except Exception:
            try:
                self.master.unbind_all("<Escape>")
            except Exception:
                pass
        self.return_to_main()

    def request_sinus(self):
        try:
            if callable(self.write_command):
                self.write_command("SINUS")
            else:
                print("SinusApp: write_command not set, skipping SINUS")
        except Exception as e:
            print(f"SinusApp: error sending SINUS: {e}")
