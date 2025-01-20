import serial
import settings
import queue
from usb_receive import USBReceive


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

    def establish_connection(self):
        try:
            # Attempt to open a serial connection on the specified port and baudrate
            self.connection = serial.Serial(self.port, self.baudrate, timeout=1)
            self.is_connected = True
            # Check the connection by sending a request
            self.check_esp_idle_response()
            return True
        except serial.SerialException as e:
            # Handle any errors that occur during connection establishment
            self.update_terminal(f"Error establishing connection: {e}")
            self.is_connected = False
            return False

    def check_esp_idle_response(self):
        if self.is_connected:

            self.waiting_for_idle = True
            self.connection.write(chr(3).encode())
            # Start the receiving loop in a background thread
            self.esp_to_queue = USBReceive(self.connection, self.data_queue)
            self.esp_to_queue.start_esp_to_queue()

    def read_queue(self):
        while not self.data_queue.empty():
            message = self.data_queue.get()
            self.dispatcher_callback(message)

            # Wait for IDLE after connection start and sending CHR(3)
            if self.waiting_for_idle and message == "IDLE":
                self.connection_established = True
                self.waiting_for_idle = False
