import os
import sys
import pynng
import json
import math

# from dynamics_platform import DynamicsPlatform
from driver_input_reader.inputs import Inputs, ControlWheel

def get_change_amount_from_wheel(wheel: ControlWheel) -> float:
    change_amount = wheel.get_change_amount()
    wheel_state = wheel.get_state()
    if wheel_state == ControlWheel.State.UP:
        return change_amount
    elif wheel_state == ControlWheel.State.DOWN:
        return -change_amount
    else:
        return 0


def send_data(pub: pynng.Pub0, payload: dict, topic: str = " ", p_print: bool = True) -> None:
    """
    publishes data via pynng

    :param pub: publisher
    :param payload: data that should be sent in form of a dictionary
    :param topic: the topic under which the data should be published  (e.g. "lap_time:")
    :param p_print: if true, the message that is sent will be printed out. Standard is set to true
    """
    json_data = json.dumps(payload)
    topic = topic + " "
    msg = topic + json_data
    if p_print is True:
        print(f"data send: {msg}")
    pub.send(msg.encode())


def read_config(config_file_path: str) -> dict:
    if os.path.isfile(config_file_path):
        with open(config_file_path, 'r') as file:
            return json.load(file)
    else:
        return create_config(config_file_path)


def create_config(config_file_path: str) -> dict:
    """wrote this to ensure that a config file always exists, ports have to be adjusted if necessary"""
    print("No Config File found, creating new one from Template")
    print("---!Using default argments for a Config file")
    template = {
        "pynng": {
            "publishers": {
                "publisher": {
                    "address": "ipc:///tmp/RAAI/driver_input_reader.ipc",
                    "topics": {
                        "driver_input": "driver_input"
                    }
                }
            },
            "subscribers": {
            }
        }
    }

    file = json.dumps(template, indent=4)
    with open(config_file_path, 'w') as f:
        f.write(file)

    return template


class DriverInputReader:
    def __init__(self, config_file = './driver_input_reader_config.json'):
        # self.dynamic_platform = DynamicsPlatform()
        self.inputs = Inputs()

        self.config = read_config(config_file)
        address = self.config["pynng"]["publishers"]["publisher"]["address"]
        self.publisher = pynng.Pub0(address)
        self.publisher.listen()

        self.platform_info = {
            "throttle": 0.0,
            "brake": 0.0,
            "clutch": 0.0,
            "steering": 0.0,
            "tilt_x": 0.0,
            "tilt_y": 0.0,
            "vibration": 0.0,
        }

    def calculate_seat_tilt(self, throttle: float, brake: float, steering: float) -> float:
        """
        Approximate calculation for what degree the Seat should tilt based on speed and steering
        """
        # formular for lateral acceleration is 'alat = (V^2)/R
        # V = velocity in m/s, R = turn radius in meter
        # tilt then equals 'angle(0) = atan(alat/g) result in radians
        if throttle >= brake:
            velocity = throttle

        elif throttle <= brake:
            velocity = -brake

        else:
            velocity = 10

        lat_acceleration = velocity**2 / (steering / 10)
        tilt_angle = math.degrees(math.atan(lat_acceleration / 9.81))
        return round(-tilt_angle, 2) / 100

    def calculate_rpm(self, throttle: float, brake: float) -> float:
        if throttle >= brake:
            velocity = throttle

        elif brake >= throttle:
            velocity = brake * 0.75

        else:
            velocity = 0

        vibration_amount = round(680.0 + (6320 * velocity / 100), 2)

        return vibration_amount

    def calculate_seat_pivot(self, throttle: float, brake: float) -> float:
        # Pivot is forward tilt
        if brake == 0.0 and throttle == 0.0:
            pivot = 0.0

        elif throttle > brake:
            pivot = throttle
        else:
            pivot = -brake

        return round(-pivot, 2)

    def handle_driver_inputs(self) -> None:
        """Reads driver inputs via pygame"""
        self.inputs.read_inputs()

        self.platform_info["throttle"] = self.inputs.get_throttle_percent()
        self.platform_info["brake"] = self.inputs.get_brake_percent()
        self.platform_info["clutch"] = self.inputs.get_clutch_percent()
        self.platform_info["steering"] = self.inputs.get_steering_percent()

    def handle_platform_inputs(self) -> None:
        """calculates theoretical platform tilt and vibration"""
        self.platform_info["tilt_x"] = self.calculate_seat_tilt(
            self.platform_info["throttle"], self.platform_info["brake"], self.platform_info["steering"]
        )

        self.platform_info["tilt_y"] = self.calculate_seat_pivot(
            self.platform_info["throttle"], self.platform_info["brake"]
        )

        self.platform_info["vibration"] = self.calculate_rpm(
            self.platform_info["throttle"], self.platform_info["brake"]
        )

    # outdated version to update the Platform. will become its own module
    # def update_platform(self):
    #     """Sets the Tilt and RPM of the Platform"""
    #     self.dynamic_platform.send_to_platform(
    #         acc_x = self.platform_info['tilt_x'],
    #         acc_y = self.platform_info['tilt_y'],
    #         rpm = self.platform_info['vibration']
    #     )

    def send_payload(self):
        """Sends Driver Data over pynng"""
        self.handle_driver_inputs()
        # Disabled because the tilt was wayy too much
        # self.handle_platform_inputs()
        topic = self.config["pynng"]["publishers"]["publisher"]["topics"]["driver_input"]
        send_data(self.publisher, self.platform_info, topic, p_print=True)

    def run(self):
        self.send_payload()
