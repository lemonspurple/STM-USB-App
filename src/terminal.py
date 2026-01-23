import os
from tkinter import Frame, Text, Scrollbar, Entry, Button, END, PhotoImage


class TerminalView:
    def __init__(self, parent, write_command=None):
        self.parent = parent
        self.write_command = write_command

        # Frame already provided as parent; create widgets inside
        self.terminal = Text(self.parent, height=15, width=30)
        self.terminal.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = Scrollbar(self.parent, command=self.terminal.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.terminal["yscrollcommand"] = self.scrollbar.set

        # placeholder icons
        self.clear_icon = None
        self.send_icon = None
        self.stop_icon = None

        # make room for input area that aligns with the terminal (excluding scrollbar)
        self.input_frame = Frame(self.parent)
        self.input_frame.grid(row=1, column=0, columnspan=1, sticky="we")
        self.input_frame.grid_columnconfigure(0, weight=1)

        # entry
        self.entry = Entry(self.input_frame)
        self.entry.grid(row=0, column=0, sticky="we", padx=(0, 4))
        self.entry.bind("<Return>", self._on_send)
        self.entry.bind("<Up>", self._history_prev)
        self.entry.bind("<Down>", self._history_next)

        # load send icon if available
        try:
            base = os.path.dirname(__file__)
            path = os.path.abspath(os.path.join(base, "assets", "icons", "refresh.png"))
            if os.path.exists(path):
                img = PhotoImage(file=path)
                # downscale if too large
                try:
                    h = img.height()
                    w = img.width()
                    max_size = 16
                    if h > max_size or w > max_size:
                        factor_h = max(1, int(h / max_size))
                        factor_w = max(1, int(w / max_size))
                        factor = max(factor_h, factor_w)
                        img = img.subsample(factor, factor)
                except Exception:
                    pass
                self.send_icon = img
                self.send_btn = Button(
                    self.input_frame,
                    image=self.send_icon,
                    command=self._on_send,
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                )
            else:
                self.send_btn = Button(
                    self.input_frame, text="Send", command=self._on_send
                )
        except Exception:
            self.send_btn = Button(self.input_frame, text="Send", command=self._on_send)
        self.send_btn.grid(row=0, column=1, pady=(0, 4))

        # stop icon (programmatic red square) next to send
        try:
            self.stop_icon = PhotoImage(width=16, height=16)
            try:
                self.stop_icon.put("#ff0000", to=(0, 0, 15, 15))
            except Exception:
                for x in range(16):
                    for y in range(16):
                        try:
                            self.stop_icon.put("#ff0000", (x, y))
                        except Exception:
                            pass
            self.stop_btn = Button(
                self.input_frame,
                image=self.stop_icon,
                command=self._on_stop,
                relief="flat",
                bd=0,
                highlightthickness=0,
            )
        except Exception:
            self.stop_btn = Button(self.input_frame, text="Stop", command=self._on_stop)
        self.stop_btn.grid(row=0, column=2, padx=(4, 0), pady=(0, 4))

        # clear button below input_frame, spanning the terminal column only
        try:
            base = os.path.dirname(__file__)
            path = os.path.abspath(os.path.join(base, "assets", "icons", "refresh.png"))
            if os.path.exists(path):
                img = PhotoImage(file=path)
                try:
                    h = img.height()
                    w = img.width()
                    max_size = 20
                    if h > max_size or w > max_size:
                        factor_h = max(1, int(h / max_size))
                        factor_w = max(1, int(w / max_size))
                        factor = max(factor_h, factor_w)
                        img = img.subsample(factor, factor)
                except Exception:
                    pass
                self.clear_icon = img
                self.clear_btn = Button(
                    self.parent,
                    image=self.clear_icon,
                    command=self.clear,
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                )
            else:
                self.clear_btn = Button(self.parent, text="Clear", command=self.clear)
        except Exception:
            self.clear_btn = Button(self.parent, text="Clear", command=self.clear)
        self.clear_btn.grid(row=2, column=0, columnspan=1, pady=10)

        # history
        self.input_history = []
        self.history_index = None

    def set_write_command(self, fn):
        self.write_command = fn

    def _store_history(self, cmd):
        try:
            if not self.input_history or self.input_history[-1] != cmd:
                self.input_history.append(cmd)
                if len(self.input_history) > 200:
                    self.input_history = self.input_history[-200:]
        except Exception:
            pass

    def _on_send(self, event=None):
        try:
            cmd = self.entry.get().strip()
            if cmd and self.write_command:
                try:
                    self.write_command(cmd)
                except Exception as e:
                    # still show error in terminal
                    self.update(f"Error sending command: {e}")
            # store history but keep input visible
            self._store_history(cmd)
            self.history_index = None
            # keep focus and place cursor at end
            try:
                self.entry.icursor(END)
                self.entry.focus_set()
            except Exception:
                pass
        except Exception as e:
            print(f"TerminalView send error: {e}")
        return "break"

    def _on_stop(self):
        try:
            # show STOP in entry
            try:
                self.entry.delete(0, END)
                self.entry.insert(0, "STOP")
                self.entry.focus_set()
                self.entry.icursor(END)
            except Exception:
                pass
            if self.write_command:
                try:
                    self.write_command("STOP")
                except Exception as e:
                    self.update(f"Error sending STOP command: {e}")
        except Exception as e:
            print(f"TerminalView stop error: {e}")

    def _history_prev(self, event=None):
        try:
            if not self.input_history:
                return "break"
            if self.history_index is None:
                self.history_index = len(self.input_history) - 1
            else:
                if self.history_index > 0:
                    self.history_index -= 1
            val = self.input_history[self.history_index]
            self.entry.delete(0, END)
            self.entry.insert(0, val)
        except Exception as e:
            print(f"TerminalView history prev error: {e}")
        return "break"

    def _history_next(self, event=None):
        try:
            if not self.input_history:
                return "break"
            if self.history_index is None:
                return "break"
            if self.history_index < len(self.input_history) - 1:
                self.history_index += 1
                val = self.input_history[self.history_index]
                self.entry.delete(0, END)
                self.entry.insert(0, val)
            else:
                self.history_index = None
                self.entry.delete(0, END)
        except Exception as e:
            print(f"TerminalView history next error: {e}")
        return "break"

    def update(self, message):
        try:
            self.terminal.insert(END, message + "\n")
            self.terminal.see(END)
        except Exception as e:
            print(f"TerminalView update error: {e}")

    def clear(self):
        try:
            self.terminal.delete(1.0, END)
        except Exception as e:
            print(f"TerminalView clear error: {e}")

    def get_input(self):
        try:
            return self.entry.get()
        except Exception:
            return ""

    def set_input(self, text):
        try:
            self.entry.delete(0, END)
            self.entry.insert(0, text)
        except Exception:
            pass

    def focus_input(self):
        try:
            self.entry.focus_set()
        except Exception:
            pass
