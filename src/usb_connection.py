import time
import serial
import settings
import queue
from usb_receive import USBReceive
import threading
import serial.tools.list_ports


class USBConnection:
    def __init__(self, update_terminal_callback, dispatcher_callback):
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

    def is_com_port_available(self):
        available_ports = [p.device for p in serial.tools.list_ports.comports()]
        return self.port in available_ports

    def establish_connection(self):
        if not self.is_com_port_available():
            self.update_terminal(f"COM port {self.port} is not available.")
            return False

        try:
            # Attempt to open a serial connection on the specified port and baudrate
            self.connection = serial.Serial(self.port, self.baudrate, timeout=1)
            self.is_connected = True
            # self.update_terminal(f"Connected to {self.port} at {self.baudrate} baud.")
            return True
        except serial.SerialException as e:
            self.is_connected = False
            self.update_terminal(f"Error establishing connection: {e}")
            return False

    def esp_restart(self):
        if self.is_connected:
            self.connection.write(chr(3).encode())

    def check_esp_idle_response(self):
        if self.is_connected:
            self.write_command("STOP")
            # self.connection.write(chr(3).encode())
            time.sleep(0.2)
            # Start the receiving loop in a background thread
            self.esp_to_queue = USBReceive(self.connection, self.data_queue)
            self.esp_to_queue.start_esp_to_queue()
            self.start_read_queue()

    def write_command(self, command):
        if self.is_connected:
            command += "\n"
            try:
                self.connection.write(command.encode())
                #self.update_terminal(f"To STM: {command}")
            except serial.SerialException as e:
                self.update_terminal(f"Error sending command: {e}")
        else:
            self.update_terminal("Not connected to any device.")

    def start_read_queue(self):
        # Start a background thread to read the queue
        self.reading_thread = threading.Thread(target=self.read_queue_loop, daemon=True)
        self.running = True
        self.reading_thread.start()

    def read_queue_loop(self):
        global STATUS
        while self.running:
            while not self.data_queue.empty():
                message = self.data_queue.get()

                # Wait for IDLE after connection start and sending CHR(3)
                if self.waiting_for_idle and message == "IDLE":
                    self.connection_established = True
                    self.waiting_for_idle = False
                    
                    
                    
                self.dispatcher_callback(message)

    def stop_read_queue(self):
        self.running = False
