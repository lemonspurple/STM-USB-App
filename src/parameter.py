import os
import sys
import time
from tkinter import Frame, Label, Button, Entry, StringVar, W, E, LabelFrame, PhotoImage


class ParameterApp:
    def __init__(self, master, write_command, return_to_main):
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main

        # Initialize the parameter dictionary
        self.parameter = {}

        # Create a frame for the ParameterApp
        self.frame_parameter = Frame(master)
        self.frame_parameter.grid(column=0, row=2, padx=20, pady=(12, 1),sticky=W)

        # Create a LabelFrame for editing parameters
        self.frame_edit = LabelFrame(master, text="Parameters")
        self.frame_edit.grid(column=0, row=1, padx=20, pady=15, sticky=W)

        # Add labels and entry fields for parameters
        self.parameter_labels_entries = []
        self.parameter_vars = {}
        parameter_keys = [
            "kP",
            "kI",
            "kD",
            "targetNa",
            "toleranceNa",
            "startX",
            "startY",
            "measureMs",
            "direction",
            "maxX",
            "maxY",
            "multiplicator",
        ]

        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        self.assets_dir = os.path.join(base_path, "assets", "icons")

        # Parameter key -> icon filename
        self.param_icon_files = {
            "kP": "icon_kP.png",
            "kI": "icon_kI.png",
            "kD": "icon_kD.png",
            "targetNa": "icon_targetNa.png",
            "toleranceNa": "icon_toleranceNa.png",
            "startX": "icon_startX.png",
            "startY": "icon_startY.png",
            "measureMs": "icon_measureMs.png",
            "direction": "icon_direction.png",
            "maxX": "icon_startX.png",
            "maxY": "icon_startY.png",
            "multiplicator": "icon_multiplicator.png",
        }

        # Cache PhotoImages to avoid garbage collected
        self.icons = {}

        self.fallback_icon = None
        fallback_path = os.path.join(self.assets_dir, "icon_unknown.png")
        if os.path.exists(fallback_path):
            try:
                self.fallback_icon = PhotoImage(file=fallback_path)
            except Exception:
                self.fallback_icon = None

        for i, key in enumerate(parameter_keys):
            icon_img = None
            icon_filename = self.param_icon_files.get(key)
            if icon_filename:
                icon_path = os.path.join(self.assets_dir, icon_filename)
                if os.path.exists(icon_path):
                    try:
                        icon_img = PhotoImage(file=icon_path)  # failsafe
                    except Exception:
                        icon_img = None

            if icon_img is None:
                icon_img = self.fallback_icon

            self.icons[key] = icon_img

            icon_label = Label(self.frame_edit, image=icon_img)
            parameter_label = Label(self.frame_edit, text=f"{key}:")
            parameter_var = StringVar()
            parameter_entry = Entry(self.frame_edit, textvariable=parameter_var)

            self.parameter_labels_entries.append((icon_label, parameter_label, parameter_entry))
            self.parameter_vars[key] = parameter_var

        # Grid the labels and entry fields for parameters
        for i, (icon_lbl, label, entry) in enumerate(self.parameter_labels_entries):
            icon_lbl.grid(column=0, row=i, padx=(4, 2), pady=1, sticky=W)
            label.grid(column=1, row=i, padx=(0, 6), pady=1, sticky=W)
            entry.grid(column=2, row=i, padx=1, pady=1)

        # Add Apply and Default buttons
        self.btn_apply_parameter_setting = Button(
            self.frame_parameter, text="Apply", command=self.apply_parameters
        )
        self.btn_apply_parameter_setting.grid(column=0, row=0, padx=1, pady=1, sticky=W)

        self.btn_set_parameter_default = Button(
            self.frame_parameter, text="Default", command=self.set_default_parameters
        )
        self.btn_set_parameter_default.grid(column=1, row=0, padx=1, pady=1, sticky=W)

        # Add Exit button to return to the main interface
        self.btn_back = Button(
            self.frame_parameter, text="Exit", command=self.return_to_main
        )
        self.btn_back.grid(column=2, row=0, padx=100, pady=1, sticky=E)

    def request_parameter(self):
        self.write_command("PARAMETER,?")

    def apply_parameters(self):
        parameters = [entry.get() for _, _, entry in self.parameter_labels_entries]
        sendstring = f"PARAMETER,{','.join(parameters)}"
        try:
            self.write_command(sendstring)
            time.sleep(0.1)
            self.request_parameter()
        except Exception as e:
            error_message = f"ERROR in apply_parameters {e}"
            print(error_message)

    def set_default_parameters(self):
        try:
            self.write_command("PARAMETER,DEFAULT")
            time.sleep(0.1)
            self.request_parameter()
        except Exception as e:
            error_message = f"ERROR in set_default_parameters {e}"
            print(error_message)

    def update_data(self, message):
        """Updates the Parameter interface with new data"""
        data = message.split(",")
        if len(data) >= 3 and data[0] == "PARAMETER":
            key = data[1]
            value = data[2]
            self.parameter[key] = value
            if key in self.parameter_vars:
                self.parameter_vars[key].set(value)
