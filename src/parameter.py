import os
import sys
import time
import json
from tkinter import (
    Frame,
    Label,
    Button,
    Entry,
    StringVar,
    W,
    E,
    LabelFrame,
    PhotoImage,
    filedialog,
    messagebox,
)
import tkinter


class ParameterApp:
    def __init__(self, master, write_command, return_to_main):
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main

        # Initialize the parameter dictionary
        self.parameter = {}

        # Create a frame for the ParameterApp
        self.frame_parameter = Frame(master)
        self.frame_parameter.grid(column=0, row=2, padx=20, pady=(12, 1), sticky=W)

        # Create a LabelFrame for editing parameters
        self.frame_edit = LabelFrame(master, text="Parameters")
        self.frame_edit.grid(column=0, row=1, padx=20, pady=15, sticky=W)

        # PARAMETERS :: Add labels and entry fields for parameters
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

        # ICONS:: Parameter key -> icon filename
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
            "save": "icon_save.png",
            "load": "icon_load.png",
        }

        # Cache PhotoImages to avoid garbage collection
        self.icons = {}
        # loading parameter icons
        self.fallback_icon = None
        fallback_path = os.path.join(self.assets_dir, "icon_unknown.png")
        if os.path.exists(fallback_path):
            try:
                self.fallback_icon = PhotoImage(file=fallback_path)
            except Exception:
                self.fallback_icon = None
        # loading ui icons
        self.ui_icons = {}
        for ui_key in ("save", "load"):
            icon_img = None
            icon_filename = self.param_icon_files.get(ui_key)
            if icon_filename:
                icon_path = os.path.join(self.assets_dir, icon_filename)
                if os.path.exists(icon_path):
                    try:
                        icon_img = PhotoImage(file=icon_path)
                    except Exception:
                        icon_img = None
            if icon_img is None:
                icon_img = self.fallback_icon
            self.ui_icons[ui_key] = icon_img

        # Saves data
        self.param_store_path = self._get_param_store_path()

        # TOOLTIPS
        self.param_tooltips = {
            "kP": "Proportional Gain: Defines how strongly the probe Z position reacts immediately to a deviation between the current and the target tunnel current.",
            "kI": "Integral Gain: Defines how strongly slow, persistent differences in the tunnel current influence the Z position over time.",
            "kD": "Derivative Gain: Defines how strongly the Z movement reacts to rapid changes in the tunnel current and helps dampen them.",
            "targetNa": "Target Tunnel Current (nA): Sets the tunnel current value around which the measurement is performed.",
            "toleranceNa": "Tunnel Current Tolerance (nA): Defines the range around the target tunnel current (targetNa) that is still considered valid tunneling.",
            "startX": "Start X Position: Specifies the X position at which the raster scan begins. Must be less than maxX.",
            "startY": "Start Y Position: Specifies the Y position at which the raster scan begins. Must be less than maxY.",
            "measureMs": "Measurement Time (ms): Defines how long the tunnel current is measured and averaged at each raster point, in milliseconds. Shortest time is 1ms.",
            "direction": "Scan Direction: Defines the direction in which the raster scan is performed along the X axis.",
            "maxX": "Maximum X Coordinate: Defines the maximum X position up to which the raster scan is executed. Value range: 1..199.",
            "maxY": "Maximum Y Coordinate: Defines the maximum Y position up to which the raster scan is executed. Value range: 1..199.",
            "multiplicator": "(BETA) Z Scaling Factor: Scales how strongly control adjustments affect the Z piezo voltage.",
        }

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

            icon_label = Label(self.frame_edit, image=icon_img)  ## Icon Label ##

            parameter_label = Label(
                self.frame_edit, text=f"{key}:"
            )  ## Parameter Itself ##
            parameter_var = StringVar()
            parameter_entry = Entry(self.frame_edit, textvariable=parameter_var)

            tip = self.param_tooltips.get(key, key)  ## Tooltip text ##
            ToolTip(icon_label, tip)
            ToolTip(parameter_label, tip)
            ToolTip(parameter_entry, tip)

            self.parameter_labels_entries.append(
                (icon_label, parameter_label, parameter_entry)
            )
            self.parameter_vars[key] = parameter_var

        # Grid the labels and entry fields for parameters
        for i, (icon_lbl, label, entry) in enumerate(self.parameter_labels_entries):
            icon_lbl.grid(column=0, row=i, padx=(4, 2), pady=1, sticky=W)
            label.grid(column=1, row=i, padx=(0, 6), pady=1, sticky=W)
            entry.grid(column=2, row=i, padx=1, pady=1)

        self.frame_files = Frame(self.frame_parameter)
        self.frame_files.grid(column=0, row=0, sticky=W)

        self.frame_actions = Frame(self.frame_parameter)
        self.frame_actions.grid(column=0, row=1, sticky=W)

        # Adding Save / Load icons
        self.btn_save_local = Button(
            self.frame_files,
            text="Save",
            image=self.ui_icons["save"],
            compound="left",
            command=self.save_parameters_to_file,
        )
        self.btn_save_local.grid(column=0, row=0, padx=1, pady=1, sticky=W)

        self.btn_load_local = Button(
            self.frame_files,
            text="Load",
            image=self.ui_icons["load"],
            compound="left",
            command=self.load_parameters_from_file,
        )
        self.btn_load_local.grid(column=1, row=0, padx=5, pady=5, sticky=W)
        # Adding Apply, Default, Exit icons
        self.btn_apply_parameter_setting = Button(
            self.frame_actions, text="Apply", command=self.apply_parameters
        )
        self.btn_apply_parameter_setting.grid(column=0, row=0, padx=1, pady=1, sticky=W)

        self.btn_set_parameter_default = Button(
            self.frame_actions, text="Default", command=self.set_default_parameters
        )
        self.btn_set_parameter_default.grid(column=1, row=0, padx=5, pady=1, sticky=W)

        self.btn_back = Button(
            self.frame_actions, text="Exit", command=self.return_to_main
        )
        self.btn_back.grid(column=2, row=0, padx=75, pady=1, sticky=E)

    def _get_param_store_path(self):
        base_dir = os.path.join(os.path.expanduser("~"), ".stm-usb-app")
        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, "parameters.json")

    def _collect_parameters_from_ui(self):
        data = {}
        for key, var in self.parameter_vars.items():
            data[key] = var.get()
        return data

    def _apply_parameters_to_ui(self, data: dict):
        for key, value in data.items():
            if key in self.parameter_vars:
                self.parameter_vars[key].set(str(value))

    def save_parameters_to_file(self):
        path = filedialog.asksaveasfilename(
            parent=self.master,
            initialfile=os.path.basename(self.param_store_path),
            initialdir=os.path.dirname(self.param_store_path),
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        self.param_store_path = path

        data = self._collect_parameters_from_ui()
        try:
            with open(self.param_store_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"ERROR in save_parameters_to_file {e}")

    def load_parameters_from_file(self):
        path = filedialog.askopenfilename(
            parent=self.master,
            initialdir=os.path.dirname(self.param_store_path),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        self.param_store_path = path

        try:
            if not os.path.exists(self.param_store_path):
                return
            with open(self.param_store_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self._apply_parameters_to_ui(data)
        except Exception as e:
            print(f"ERROR in load_parameters_from_file {e}")

    def request_parameter(self):
        self.write_command("PARAMETER,?")

    def apply_parameters(self):
        # Validate numeric constraints for start/max coordinates before sending
        def _get_int(name):
            var = self.parameter_vars.get(name)
            if var is None:
                raise ValueError(f"{name} missing")
            val = var.get()
            return int(val)

        try:
            maxX = _get_int("maxX")
            maxY = _get_int("maxY")
            startX = _get_int("startX")
            startY = _get_int("startY")
        except ValueError as e:
            messagebox.showerror("Parameter error", f"Invalid value: {e}")
            return
        except Exception:
            messagebox.showerror(
                "Parameter error",
                "startX/startY/maxX/maxY must be integer values.",
            )
            return

        if not (1 <= maxX <= 199 and 1 <= maxY <= 199):
            messagebox.showerror(
                "Parameter error", "maxX and maxY must be between 1 and 199."
            )
            return

        if not (startX < maxX and startY < maxY):
            messagebox.showerror(
                "Parameter error",
                "startX must be less than maxX and startY must be less than maxY.",
            )
            return

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


## Tooltips for parameters ##
import tkinter as tk


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show, add="+")
        widget.bind("<Leave>", self.hide, add="+")

    def show(self, event=None):
        if self.tip or not self.text:
            return
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)  # kein Fensterrahmen
        self.tip.attributes("-topmost", True)

        label = tk.Label(
            self.tip, text=self.text, borderwidth=1, relief="solid", padx=6, pady=4
        )
        label.pack()

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tip.geometry(f"+{x}+{y}")

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None
