import threading
import queue


class USBReceive:
    def __init__(self, connection, data_queue):
        self.connection = connection
        self.data_queue = data_queue
        self.running = False

    def start_esp_to_queue(self):
        self.running = True
        threading.Thread(target=self.esp_to_queue_loop, daemon=True).start()

    def stop_receiving(self):
        self.running = False

    def esp_to_queue_loop(self):
        while self.running:
            response = self.connection.readline().decode().strip()
            if response:
                self.data_queue.put(response)
