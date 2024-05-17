class Button:

    def __init__(self, pin: int, bounce_time: float):
        self.when_pressed = None
        print(f'init fake button in GPIO pin: {pin}')

