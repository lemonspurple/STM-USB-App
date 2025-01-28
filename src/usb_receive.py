import threading


class USBReceive:
    def __init__(self, connection, data_queue):
        self.connection = connection
        self.data_queue = data_queue
        self.running = False

    def start_esp_to_queue(self):
        self.running = True
        threading.Thread(target=self.esp_to_queue, daemon=True).start()

    def stop_esp_to_queue(self):
        self.running = False

    def esp_to_queue(self):
        while self.running:
            try:
                response = self.connection.readline().decode().strip()
                if response:
                    self.data_queue.put(response)
            except Exception as e:
                print(f"Error in esp_to_queue: {e}")
                self.running = False
                # Optionally, re-raise the exception to see the full traceback
                raise
