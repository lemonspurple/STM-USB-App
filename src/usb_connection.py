import time
import serial
import settings
import queue
import threading
import serial.tools.list_ports


class USBConnection:
    def __init__(self, update_terminal_callback, dispatcher_callback):
        # Initialize USBConnection with callbacks and settings
        self.port = settings.USB_PORT
        self.baudrate = settings.USB_BAUDRATE
        self.connection = None
        self.is_connected = False
        self.update_terminal = update_terminal_callback
        self.dispatcher_callback = dispatcher_callback
        self.connection_established = False
        self.data_queue = queue.Queue()
        self.esp_to_queue = None
        self.waiting_for_idle = False
        self.running = False
        self.receive_running = False

    def is_com_port_available(self):
        # Check if the specified COM port is available
        available_ports = [p.device for p in serial.tools.list_ports.comports()]
        return self.port in available_ports

    def establish_connection(self):
        # Establish a connection to the specified COM port
        if not self.is_com_port_available():
            self.update_terminal(f"COM port {self.port} is not available.")
            return False

        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=1)
            self.is_connected = True
            return True
        except serial.SerialException as e:
            self.is_connected = False
            self.update_terminal(f"Error establishing connection: {e}")
            return False

    def esp_restart(self):
        # Send a restart command (Ctrl+C) to the ESP device
        if self.is_connected:
            self.connection.write(chr(3).encode())

    def check_esp_idle_response(self):
        # Check if the ESP device is in idle state
        if self.is_connected:
            self.write_command("STOP")
            time.sleep(0.2)
            self.start_esp_to_queue()
            self.start_read_queue()

    def write_command(self, command):
        # Write a command to the ESP device
        if self.is_connected:
            try:
                self.connection.write((command + "\n").encode())
                self.update_terminal(f"To STM: {command}")
            except serial.SerialException as e:
                self.update_terminal(f"Error sending command: {e}")
        else:
            self.update_terminal("Not connected to any device.")

    ############# Consume queue 
    def start_read_queue(self):
        # Start a background thread to read the data queue
        self.reading_thread = threading.Thread(target=self.read_queue_loop, daemon=True)
        self.running = True
        self.reading_thread.start()

    def read_queue_loop(self):
        # Loop to read messages from the data queue and dispatch them
        global STATUS
        while self.running:
            while not self.data_queue.empty():
                message = self.data_queue.get()
                if self.waiting_for_idle and message == "IDLE":
                    self.connection_established = True
                    self.waiting_for_idle = False
                self.dispatcher_callback(message)

    def stop_read_queue(self):
        # Stop the read queue loop
        self.running = False

    
    ################ ESP to queue block
    def start_esp_to_queue(self):
        # Start the ESP to queue thread
        self.receive_running = True
        threading.Thread(target=self.esp_to_queue_loop, daemon=True).start()

    def stop_esp_to_queue(self):
        # Stop the ESP to queue thread
        self.receive_running = False

    def esp_to_queue_loop(self):
        # Loop to read responses from the ESP device and put them in the data queue
        
        while self.receive_running:
            try:
                response = self.connection.readline().decode().strip()
                if response:
                    self.data_queue.put(response)
            except Exception as e:
                print(f"Error in esp_to_queue: {e}")
                self.receive_running = False
                raise
