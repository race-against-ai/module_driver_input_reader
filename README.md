# **RAAI Module: Driver Input Reader**  
This module is responsible for reading driver input data from a controller. The input data includes actions such as steering, throttle, brake, clutch, and button presses. Additional platform-specific data, such as tilt or vibration, is also sent with the driver input data.  

---

## **Setup**  

### **Prerequisites**  
- Ensure that you have a compatible controller connected, which is recognizable by Pygame.  
- Additional details about supported controllers and setup can be found in `inputs.py`.  

### **Starting the Module**  
1. Launch the module via its executable or by running `main.py`.  
2. For testing other dependent modules:  
   - Use the `test_data_send.py` script inside the `driver_input_reader` directory to simulate platform data.  
   - This script sends mock platform data over the same PyNNG address.  

---

## **Data Communication**  
- **PyNNG Address**:  
  `ipc:///tmp/RAAI/driver_input_reader.ipc`  

- **Topic**:  
  `"driver_input"`  

This address is used to send the driver input data to other modules.  

---

## **Controller Initialization**  

The `Inputs` class initializes the following devices:  
- **Steering Controller**  
- **Pedals Controller**  
- **Optional Button Controller**  

When the program starts:  
1. Available devices are listed.  
2. Devices are matched based on their names:  
   - `"SimuCUBE"` → Steering device.  
   - `"BU0836A Interface"` → Pedals device.  
   - `"Ssrg Competition 300-V2"` → Buttons device (optional).  
3. If either the steering or pedal controller is not connected, the program will exit with an error.  

---

## **Control Wheels**  
Control wheels are used for fine adjustments. Each control wheel can handle:  
- **Button Press States**:  
  - `UP` → Button pressed for an increase.  
  - `DOWN` → Button pressed for a decrease.  
  - `IDLE` → No button pressed.  

- **Timeouts**: Prevent rapid repeated inputs by setting time intervals between actions.  

The following control wheels are defined:  
- **Throttle, Brake, Clutch, and Steering**  
- **Overall Control Wheel** (for general adjustments)  
- **Platform and Offset Buttons**  

---

## **Reading Inputs**  

### **Axis Inputs**  
The `Inputs` class reads the following axis inputs from the controllers:  
- **Steering Axis**: Left (-1) to Right (+1).  
- **Throttle Axis**: Normalized percentage [0%-100%].  
- **Brake Axis**: Normalized percentage [0%-100%].  
- **Clutch Axis**: Normalized percentage [0%-100%].  

### **Button Inputs**  
Button states are checked individually, such as for shift buttons or specific platform controls.  

---

## **Key Methods**  

### **Initialization**  
- `init_devices()`: Initializes connected devices and assigns roles based on their names.  

### **Reading Inputs**  
- `read_inputs()`: Updates the current state of steering, throttle, brake, and clutch axes.  

### **Data Conversion**  
- `get_steering_percent()`: Returns steering percentage (scaled).  
- `get_throttle_percent()`, `get_brake_percent()`, `get_clutch_percent()`: Normalize and scale inputs to percentages.  

### **Control Adjustments**  
- Each control wheel has a `get_state()` method to determine its current state (`UP`, `DOWN`, or `IDLE`).  
- `get_change_amount()`: Returns the magnitude of adjustment for a control wheel.  
