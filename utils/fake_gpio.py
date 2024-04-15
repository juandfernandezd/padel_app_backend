class FakeGPIO:
    BCM = 'BCM'
    IN = 'IN'

    @staticmethod
    def setmode(mode: str):
        pass
    
    @staticmethod
    def setup(pin: int, port_type: str):
        pass