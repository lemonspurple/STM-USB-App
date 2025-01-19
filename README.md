# Tkinter USB App

This project is a Tkinter-based application designed to establish a USB connection with an ESP32 device. It allows users to choose between two main functionalities: MEASURE and ADJUST. The application provides real-time feedback from the ESP32 and offers a user-friendly interface for managing tasks.

## Project Structure

```
tkinter-usb-app
├── src
│   ├── main.py          # Entry point of the application
│   ├── measure.py       # GUI for MEASURE functionality
│   ├── adjust.py        # GUI for ADJUST functionality
│   └── usb_connection.py # Manages USB connection to ESP32
├── requirements.txt     # Lists project dependencies
└── README.md            # Documentation for the project
```

## Features

- Establishes a USB connection with an ESP32 device.
- Real-time display of responses from the ESP32.
- User can select between MEASURE and ADJUST functionalities.
- Modular design with separate files for different functionalities.

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/tkinter-usb-app.git
   cd tkinter-usb-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Usage Guidelines

- Upon starting the application, it will attempt to establish a USB connection with the ESP32.
- If the connection is successful and the ESP32 responds with "IDLE", you can choose between MEASURE and ADJUST.
- The MEASURE functionality allows you to perform measurement tasks and view real-time data.
- The ADJUST functionality provides controls for adjusting parameters as needed.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.