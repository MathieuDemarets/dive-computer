import yaml
from yaml.loader import SafeLoader

class Bottle:
    def __init__(self, volume, pressure, type:str="air", ppO2:float=0.21, ppN2:float=0.79,
        reserve:int=50):
        self._volume = volume  
        self._pressure = pressure
        self._remaining_pressure = pressure
        self._type = type
        self._ppO2 = ppO2
        self._ppN2 = ppN2
        self._reserve = reserve

    @classmethod
    def from_yaml(cls, yaml_path: str):
        with open(yaml_path, "r") as yaml_file:
            params = yaml.load(yaml_file, Loader=SafeLoader)
        return cls(
            volume=params["bottle"]["volume"],
            pressure=params["bottle"]["pressure"],
            type=params["bottle"].get("type", "air"),
            ppO2=params["bottle"].get("ppO2", 0.21),
            ppN2=params["bottle"].get("ppN2", 0.79),
            reserve=params["bottle"].get("reserve", 50)
        )

    @property
    def total_gas_volume(self):
        return self._volume * self._pressure
    
    @property
    def remaining_gas_volume(self):
        return self._volume * self._remaining_pressure
    
    @property
    def remaining_pressure(self):
        return self._remaining_pressure

    @remaining_pressure.setter
    def remaining_pressure(self, value):
        """
        Set the remaining pressure in the bottle.

        Parameters:
        - value (float): The new remaining pressure in bar.

        Raises:
        - ValueError: If the remaining pressure is set below 0.
        """
        if value < 0:
            raise ValueError("Remaining pressure cannot be below 0.")
        self._remaining_pressure = value
    
    def use_gas(self, amount:int, unit:str="bar", safe:bool=True):
        """
        Use a specified amount of gas from the bottle.

        Parameters:
        - amount (int): The amount of gas to use.
        - unit (str): The unit of the amount ("bar" or "L").
        - safe (bool): Whether to respect the reserve limit.

        Raises:
        - ValueError: If there is not enough gas remaining in the bottle.
        """
        limit_pressure = self._reserve if safe else 0
        pressure_drop = amount if unit == "bar" else amount / self._volume
        if self._remaining_pressure - pressure_drop < limit_pressure:
            raise ValueError(f"Not enough gas remaining in the bottle ({self._remaining_pressure} bar remaining, {pressure_drop} bar requested, {limit_pressure} bar minimum).")
        self.remaining_pressure -= pressure_drop