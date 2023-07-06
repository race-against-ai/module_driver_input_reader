# RAAI Module Driver Input Reader
RAAI Module responsible for Reading Driver Input Data

## Setup
The Actual Setup will need some sort of controller which Pygame can recognize. More Details can be found in inputs.py <br>

Additional Data like the expected Platform Tilt or Vibration will also be sent over with the Driver Input Data

Either start the module with its Executable or over the main.py

If you need to test another Module dependent on this one, use the ``test_data_send.py`` inside ``driver_input_reader``<br>
its purpose is to send over faux Platform data over the same pynng address if needed <br>

## Structure
The Data received from the platform will be sent over the pynng address ``"ipc:///tmp/RAAI/driver_input_reader.ipc"`` 
with the topic ``"driver_input"``
