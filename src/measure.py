from tkinter import Frame, Text, Button, END

class MeasureApp:
    def __init__(self, master, write_command, return_to_main):
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main
       
        
        self.frame = Frame(master)
        self.frame.pack()

        self.terminal_output = Text(self.frame, height=15, width=50)
        self.terminal_output.pack()

        self.measure_button = Button(self.frame, text="Start Measurement", command=self.start_measurement)
        self.measure_button.pack()

        self.quit_button = Button(self.frame, text="Quit", command=master.quit)
        self.quit_button.pack()

    
    def request_measure(self):
        self.write_command("MEASURE")
        
        
    def start_measurement(self):
        # Logic to start measurement and display real-time data
        pass

    def update_terminal(self, message):
        self.terminal_output.insert(END, message + "\n")
        self.terminal_output.see(END)