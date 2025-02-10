# ESP32 to PC

## class USBConnection (usb_connection.py) 
self.data_queue = queue.Queue() 

### esp_to_queue_loop
connection.readline() -->  data_queue.put

### read_queue_loop
mot data_queue.empty() --> line --> dipatcher_callback(line) -->dispatch_received_data   
time.sleep(0.001)



## class MainGui (main.py)

### dispatch_received_data   
"DATA" 
- DONE
- measure_app.update_data
- update_terminal "Processing Y"


