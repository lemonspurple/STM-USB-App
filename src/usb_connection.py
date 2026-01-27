"""Simple USB serial connection helper used by the GUI.

Responsibilities:
- open/close serial connection
- background reader thread that pushes incoming lines into a queue
- background dispatcher thread that consumes the queue and forwards
    lines to the application's dispatcher

The class keeps lightweight thread management: threads are stored and
joined on close to avoid background threads lingering after shutdown.
"""

import queue
import threading
import time

import serial
from serial import SerialException

import config_utils


class USBConnection:
    def __init__(self, update_terminal_callback, dispatcher_callback):
        # Initialize USBConnection with callbacks and settings
        self.update_terminal = update_terminal_callback
        self.dispatcher_callback = dispatcher_callback
        self.connection = None
        self.is_connected = False
        self.connection_established = False
        self.data_queue = queue.Queue()
        self.esp_to_queue = None
        self.waiting_for_idle = False
        self.running = False
        self.receive_running = False
        # thread handles so we can join on stop/close
        self.reading_thread = None
        self.esp_thread = None
        self.port = config_utils.get_config("USB", "port")
        self.baudrate = config_utils.get_config("USB", "baudrate") or 460800

    def establish_connection(self):
        try:
            self.connection = serial.Serial(
                self.port, self.baudrate, timeout=1, write_timeout=1
            )
            self.is_connected = True
            self.connection_established = True
            return True
        except serial.SerialTimeoutException as e:
            self.is_connected = False
            error_msg = f"Connection timeout on port {self.port}: {e}"
            self.update_terminal(error_msg)
            print(f"ERROR establish_connection timeout: {error_msg}")
            return False
        except SerialException as e:
            self.is_connected = False
            msg = str(e)
            suggestions = (
                "Possible causes: another program has the port open (serial monitor, IDE), "
                "insufficient permissions, or a driver/OS issue. Try:\n"
                " - Close other serial programs (Arduino IDE, PuTTY, VSCode serial monitor)\n"
                " - Run this program as Administrator\n"
                " - Reconnect the USB device or reboot the PC\n"
                " - Check Device Manager for driver issues and the COM number\n"
                " - Use Sysinternals 'handle.exe -a COM8' to find which process holds the port"
            )
            error_msg = (
                f"Serial connection error on port {self.port}: {msg}\n{suggestions}"
            )
            self.update_terminal(error_msg)
            print(f"ERROR establish_connection: {error_msg}")
            return False
        except Exception as e:
            self.is_connected = False
            error_msg = f"Unexpected error connecting to {self.port}: {e}"
            self.update_terminal(error_msg)
            print(f"ERROR establish_connection unexpected: {error_msg}")
            return False

    def esp_restart(self):
        # Send a restart command (Ctrl+C) to the ESP device
        if self.is_connected:
            try:
                # send STOP line (device expects newline-terminated commands)
                self.connection.write(b"STOP\n")
            except Exception as e:
                self.update_terminal(f"Error sending restart to ESP: {e}")

    def start_receiving(self):
        if self.is_connected:
            self.start_esp_to_queue()
            self.start_read_queue()
            return True
        else:
            return False

    def write_command(self, command):
        # Write a command to the ESP device
        if not self.is_connected or not self.connection:
            self.update_terminal("Not connected to any device.")
            return False

        try:
            self.connection.write((command + "\n").encode())
            self.update_terminal(f"To STM: {command}")
            return True
        except serial.SerialTimeoutException as e:
            self.update_terminal(f"Timeout error sending command: {e}")
            print(f"ERROR write_command timeout {e}")
            return False
        except SerialException as e:
            self.update_terminal(f"Error sending command: {e}")
            print(f"ERROR write_command {e}")
            return False
        except Exception as e:
            self.update_terminal(f"Unexpected error sending command: {e}")
            print(f"ERROR write_command unexpected {e}")
            return False

    # Consume queue
    def start_read_queue(self):
        # Start a background thread to read the data queue
        if self.reading_thread and self.reading_thread.is_alive():
            return
        self.running = True
        self.reading_thread = threading.Thread(target=self.read_queue_loop, daemon=True)
        self.reading_thread.start()

    def read_queue_loop(self):
        # Loop to read messages from the data queue and dispatch them
        global STATUS
        buffer = ""
        while self.running:
            while not self.data_queue.empty():
                buffer += (
                    self.data_queue.get() + "\n"
                )  # Add newline to simulate complete lines
                lines = buffer.split("\n")
                buffer = lines.pop()  # Keep the last partial line in the buffer

                if lines:
                    self.dispatcher_callback("\n".join(lines))
            # prevent busy-spin
            time.sleep(0.01)

    def stop_read_queue(self):
        # Stop the read queue loop
        self.running = False
        # join thread to ensure clean stop
        try:
            if self.reading_thread:
                self.reading_thread.join(timeout=0.5)
        except Exception:
            pass

    def queue_is_empty(self):
        # Check if the data queue is empty
        return self.data_queue.empty()

    # ESP to queue
    def start_esp_to_queue(self):
        # Start the ESP to queue thread
        if self.esp_thread and self.esp_thread.is_alive():
            return
        self.receive_running = True
        self.esp_thread = threading.Thread(target=self.esp_to_queue_loop, daemon=True)
        self.esp_thread.start()

    def esp_to_queue_loop(self):
        # Loop to read responses from the ESP device and put them in the data queue
        buffer = ""
        while self.receive_running:
            try:
                # Read available data from the serial port
                if not self.connection:
                    time.sleep(0.01)
                    continue

                in_wait = 0
                try:
                    in_wait = self.connection.in_waiting
                except Exception:
                    in_wait = 0

                if in_wait > 0:
                    raw = self.connection.read(in_wait)
                    try:
                        buffer += raw.decode(errors="replace")
                    except Exception:
                        buffer += str(raw)
                    lines = buffer.split("\n")
                    buffer = lines.pop()  # Keep the last partial line in the buffer

                    for line in lines:
                        if line.strip():
                            self.data_queue.put(line.strip())
            except Exception as e:
                # Log the error, stop receiving and inform the UI
                print(f"Error in esp_to_queue: {e}")
                self.update_terminal(f"Error reading from serial: {e}")
                self.receive_running = False
                break

    def stop_esp_to_queue(self):
        # Stop the ESP to queue loop
        self.receive_running = False
        try:
            if self.esp_thread:
                self.esp_thread.join(timeout=0.5)
        except Exception:
            pass

    def close_connection(self):
        # Close the USB connection and stop all threads
        self.stop_read_queue()
        self.stop_esp_to_queue()
        try:
            if self.connection and getattr(self.connection, "is_open", False):
                self.connection.close()
        except Exception:
            pass
        self.is_connected = False
        self.connection_established = False
