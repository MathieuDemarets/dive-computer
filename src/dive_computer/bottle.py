class Bottle:
    def __init__(self, volume, pressure):
        self.volume = volume  
        self.pressure = pressure

    @property
    def total_gas(self):
        return self.volume * self.pressure