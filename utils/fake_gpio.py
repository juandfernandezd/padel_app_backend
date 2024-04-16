class Button:

    def __init__(self, pin: int):
        self.when_pressed = None
        print(f'init fake button in GPIO pin: {pin}')

