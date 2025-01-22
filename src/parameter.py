from tkinter import Frame, Label, Button, Entry, StringVar

class ParameterApp:
    def __init__(self, master, write_command):
        self.master = master
        self.write_command = write_command

        # Create a frame for the ParameterApp
        self.frame = Frame(master)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add a label for the parameter
        self.parameter_label = Label(self.frame, text="Parameter:")
        self.parameter_label.pack(pady=5)

        # Add an entry widget for the parameter
        self.parameter_var = StringVar()
        self.parameter_entry = Entry(self.frame, textvariable=self.parameter_var)
        self.parameter_entry.pack(pady=5)

        # Add a button to send the parameter
        self.send_button = Button(self.frame, text="Send", command=self.send_parameter)
        self.send_button.pack(pady=5)

        # Add a status label
        self.status_label = Label(self.frame, text="Status: Waiting for input...")
        self.status_label.pack(pady=5)

    def send_parameter(self):
        parameter = self.parameter_var.get()
        sendstring = f"PARAMETER,{parameter}\n"
        try:
            self.write_command(sendstring)
            self.status_label.config(text="Status: Parameter sent!")
        except Exception as e:
            error_message = f"ERROR in send_parameter {e}"
            self.status_label.config(text=error_message)

    def update_data(self, message):
        """Updates the Parameter interface with new data"""
        data = message.split(',')
        if data[0] == 'PARAMETER':
            # Update the status label with the received data
            self.status_label.config(text=f"Received: {data[1]}")