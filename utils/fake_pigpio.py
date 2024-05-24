INPUT = 0
PUD_UP = 2
EITHER_EDGE = 1

class pi:

    def __init__(self):
        print(f'init fake pi')

    def set_mode(self, pin: int, mode: int):
        print(f'pin {pin} ::: mode {mode}')

    def set_pull_up_down(self, pin: int, mode: int):
        print(f'pin {pin} ::: mode {mode}')

    def callback(self, pin: int, mode: int, func):
        print(f'pin {pin} ::: mode {mode}')


