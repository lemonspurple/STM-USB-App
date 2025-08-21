# Tkinter USB App

This project is a Tkinter-based application designed to establish a USB connection with the ESP32 device on 500 EURO RTM. 


## Setup Instructions

1. Clone the repository into folder 500_RTM:
   ```
   cd 500_RTM
   git clone https://github.com/PeterDirnhofer/tkinter-usb-app.git
   ```


2. Create and activate a virtual environment named .venv:
   **On Windows:**
   ```sh
   cd tkinter-usb-app
   python -m venv .venv
   .venv\Scripts\activate
   ```

   **On macOS/Linux:**
   ```sh
   cd tkinter-usb-app
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required dependencies (make sure your environment is activated):
   ```sh
   pip install -r requirements.txt
   ```


## Run the Project in Visual Studio Code


### Open the Project in Visual Studio Code

From your project directory, open the `tkinter-usb-app` folder in Visual Studio Code by running:

```sh
cd tkinter-usb-app
code .
```

> **Note:** Be sure to use `code .` (with the dot) to open the current folder in VS Code. Using only `code` will not open the folder as a project.

## Run the Program

Select `main.py` in `src` folder . Click the **Run** button (Run Python File) to start the application.

## Usage Guidelines

- When you start the application, it will automatically attempt to establish a USB connection with the ESP32 device.
- If the connection is successful and the ESP32 responds with **"IDLE"**, you can select from the following main functionalities:
   - **Measure:** Perform measurement tasks and view real-time data from the device.
   - **Parameter:** Access controls for adjusting device parameters as needed.
   - **Tools:** Access additional utilities for device management and diagnostics, such as:
      - Manually set Hardware DACs and read ADC
      - Make DACs to output a sinus
      - **Init Tunnel Current:** Set DAC Z to establish  tunnel contact.
      - **Show Measurement During Tunnel Contact:** Display real-time measurement data as the device establishes tunnel contact.



## License

This project is licensed under the MIT License. See the LICENSE file for more details.
