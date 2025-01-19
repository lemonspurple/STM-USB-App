import threading
import queue

class USBReceive:
    def __init__(self, connection, data_queue):
        self.connection = connection
        self.data_queue = data_queue
        self.running = False

    def start_receiving(self):
        self.running = True
        threading.Thread(target=self.receive_loop, daemon=True).start()

    def stop_receiving(self):
        self.running = False

    def receive_loop(self):
        while self.running:
            response = self.connection.readline().decode().strip()
            if response:
                self.data_queue.put(response)