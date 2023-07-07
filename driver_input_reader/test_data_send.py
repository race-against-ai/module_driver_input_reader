import pynng
import json
from time import sleep
import math
# Script for sending faux Platform Data. Only used for testing purposes

PYNNG_PLATFORM_ADDRESS = "ipc:///tmp/RAAI/driver_input_reader.ipc"


def calculate_seat_tilt(throttle, brake, steering) -> float:
    """
    Approximate calculation for what degree the Seat should tilt based on speed and steering
    """
    if throttle >= brake:
        velocity = throttle

    elif throttle <= brake:
        velocity = -brake

    else:
        velocity = 0

    lat_acceleration = velocity ** 2 / steering
    tilt_angle = math.degrees(math.atan(lat_acceleration / 9.81))
    return round(-tilt_angle, 2)


def calculate_rpm(throttle, brake) -> float:
    if throttle >= brake:
        velocity = throttle

    elif brake >= throttle:
        velocity = brake*0.75

    else:
        velocity = 0
    vibration_amount = round(680.0 + (6320 * velocity / 100), 2)

    return vibration_amount


def calculate_seat_pivot(throttle, brake) -> float:
    # Pivot is forward tilt
    if brake == 0 and throttle == 0:
        pivot = 0

    elif throttle > brake:
        pivot = throttle
    else:
        pivot = -brake

    return round(-pivot, 2)


def send_data(pub: pynng.Pub0, payload: dict, topic: str = " ", p_print: bool = True) -> None:
    """
    publishes data via pynng

    :param pub: publisher
    :param payload: data that should be sent in form of a dictionary
    :param topic: the topic under which the data should be published  (e.g. "lap_time: ")
    :param p_print: if true, the message that is sent will be printed out. Standard is set to true
    """
    json_data = json.dumps(payload)
    msg = topic + json_data
    if p_print is True: print(f"data send: {msg}")
    pub.send(msg.encode())


if __name__ == '__main__':
    payload = {
        'throttle': 0.0,
        'brake': 0.0,
        'clutch': 0.0,
        'steering': 0.0,
        'tilt_x': 0.0,
        'tilt_y': 0.0,
        'vibration': 0.0
    }
    with pynng.Pub0() as pub:
        pub.listen(PYNNG_PLATFORM_ADDRESS)
        while True:
            send_data(pub, payload, "driver_input ", p_print=True)
            payload['throttle'] += 0.5
            if payload['throttle'] >= 100:
                payload['throttle'] = 100

            payload['brake'] += 0.3
            if payload['brake'] >= 100:
                payload['brake'] -= 100

            payload['clutch'] += 0.1
            if payload['clutch'] >= 100:
                payload['clutch'] -= 100

            payload['steering'] += 0.8
            if payload['steering'] >= 100:
                payload['steering'] -= 200

            payload['tilt_y'] = calculate_seat_pivot(payload['throttle'], payload['brake'])

            payload['tilt_x'] = calculate_seat_tilt(payload['throttle'], payload['brake'], payload['steering'])

            payload['vibration'] = calculate_rpm(payload['throttle'], payload['brake'])

            sleep(1/10)


