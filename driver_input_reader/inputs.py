import enum
import sys
import pygame
import time


class ControlWheel:
    class State(enum.Enum):
        IDLE = 0
        UP = 1
        DOWN = 2

    def __init__(
        self,
        joystick: pygame.joystick.JoystickType,
        button_up: int,
        button_down: int,
        timeout: float = 0.1,
        change_amount: float = 5.0,
    ) -> None:
        self.joystick = joystick
        self.button_up = button_up
        self.button_down = button_down
        self.timeout = timeout
        self.last_timestamp = 0.0
        self.change_amount = change_amount

    def get_state(self) -> State:
        current_timestamp = time.time()
        if current_timestamp - self.last_timestamp > self.timeout:
            if self.button_up is not None and self.joystick.get_button(self.button_up):
                self.last_timestamp = current_timestamp
                return self.State.UP
            elif self.button_down is not None and self.joystick.get_button(self.button_down):
                self.last_timestamp = current_timestamp
                return self.State.DOWN

        return self.State.IDLE

    def get_change_amount(self) -> float:
        return self.change_amount


class Inputs:
    def __init__(self):
        self.pedals = None
        self.steer = None
        self.buttons = None

        self.throttle_control_wheel = None
        self.brake_control_wheel = None
        self.clutch_control_wheel = None
        self.steering_control_wheel = None
        self.overall_control_wheel = None

        self.platform_button = None
        self.head_reset_button = None
        self.head_change_button = None
        self.pedal_button = None

        self.offset_set = None
        self.offset_control_wheel = None
        self.offset_reset = None

        self.steering_axis = 0
        self.throttle_axis = 0
        self.brake_axis = 0
        self.clutch_axis = 0

        pygame.init()
        pygame.joystick.init()

        self.init_devices()

    def init_devices(self):
        print("available devices:")
        for x in range(pygame.joystick.get_count()):
            current_joystick = pygame.joystick.Joystick(x)
            print("\t" + current_joystick.get_name())

            match current_joystick.get_name():
                case "SimuCUBE":
                    self.steer = current_joystick
                case "BU0836A Interface":
                    self.pedals = current_joystick
                case "Ssrg Competition 300-V2":
                    self.buttons = current_joystick

        if self.pedals is None or self.steer is None:
            # if any of the two aren't connected, exit
            print("A critical input is missing")
            print("pedals is {}".format(self.pedals))
            print("steering is {}".format(self.steer))
            sys.exit(-1)

        # initialize the required joysticks
        self.pedals.init()
        self.steer.init()

        print()
        print("steering is " + self.steer.get_name())
        print("pedals are " + self.pedals.get_name())

        # the buttons are optional
        if self.buttons is None:
            print("steering wheel buttons unavailable")
        else:
            print("buttons are {}".format(self.buttons.get_name()))
            self.buttons.init()

        self.throttle_control_wheel = ControlWheel(self.buttons, 5, 4)
        self.brake_control_wheel = ControlWheel(self.buttons, 3, 2)
        self.clutch_control_wheel = ControlWheel(self.buttons, 21, 20)
        self.steering_control_wheel = ControlWheel(self.buttons, 24, 25)
        self.overall_control_wheel = ControlWheel(self.buttons, 0, 1, timeout=0.3)

        self.platform_button = ControlWheel(self.buttons, 6, None, timeout=0.5)
        self.head_reset_button = ControlWheel(self.buttons, 22, None, timeout=0.5)
        self.head_change_button = ControlWheel(self.buttons, 28, None, timeout=0.5)
        self.pedal_button = ControlWheel(self.buttons, 10, None, timeout=0.5)

        self.offset_set = ControlWheel(self.buttons, 14, None, timeout=0.5)
        self.offset_control_wheel = ControlWheel(self.buttons, 9, 8, change_amount=1)
        self.offset_reset = ControlWheel(self.buttons, 16, None, timeout=0.5)

    def read_inputs(self):
        for event in pygame.event.get():
            pass
        self.steering_axis = self.steer.get_axis(0)
        self.throttle_axis = self.pedals.get_axis(0)
        self.brake_axis = self.pedals.get_axis(1)
        self.clutch_axis = self.pedals.get_axis(2)

    def get_steering_percent(self) -> float:
        # left: -1, right: 1
        # TODO: move negation and offset to the sending process
        #       this here moves the display in the wrong direction as well as creating an offset
        #       the middle is also moved, creting a deadzone, which is not in the center
        return self.steering_axis * -100.0

    def get_throttle_percent(self) -> float:
        # -1 - 0.32                D: 1.32
        return (self.throttle_axis + 1) / 1.32 * 100.0

    def get_brake_percent(self) -> float:
        # -0.8 - -0.2              D: 0.6
        return (self.brake_axis + 0.78) / 0.58 * 100.0

    def get_clutch_percent(self) -> float:
        # -1 - 0.83233642578125    D: 1.83233
        return (self.clutch_axis + 1) / 1.83233642578125 * 100.0

    def get_steering_percent_scaled(self, max: float) -> float:
        # left: -1, right: 1
        value = self.get_steering_percent()
        if 5 > value > -5:
            value = 0
        return value * (max / 100.0)

    def get_throttle_percent_scaled(self, max: float) -> float:
        value = self.get_throttle_percent()
        if value < 1.0:
            value = 0.0
        return value * (max / 100.0)

    def get_brake_percent_scaled(self, max: float) -> float:
        value = self.get_brake_percent()
        if value < 5:
            value = 0
        return value * (max / 100.0)

    def get_clutch_percent_scaled(self, max: float) -> float:
        value = self.get_clutch_percent()
        if value < 1.0:
            value = 0.0
        return value * (max / 100.0)

    #
    # Buttons
    #
    def is_shift_button_left_pressed(self):
        return self.is_button_pressed(7)

    def is_shift_button_right_pressed(self):
        return self.is_button_pressed(23)

    def is_button_pressed(self, button: int):
        if self.buttons:
            return self.buttons.get_button(button)
        return False
