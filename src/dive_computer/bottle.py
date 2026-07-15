import yaml
from yaml.loader import SafeLoader
import pandas as pd

class Bottle:
    """
    A class representing a diving bottle with properties such as volume, pressure, and gas composition.
    Attributes:
        volume (float): The volume of the bottle in liters.
        pressure (float): The initial pressure of the bottle in bar.
        type (str): The type of gas in the bottle (default is "air").
        ppO2 (float): The partial pressure of oxygen in the gas mixture (default is 0.21).
        ppN2 (float): The partial pressure of nitrogen in the gas mixture (default is 0.79).
        reserve (int): The reserve pressure in bar (default is 50).
        remaining_pressure (float): The remaining pressure in the bottle in bar.
        pressure_log (pd.DataFrame): A log of the remaining pressure over time.
    Class Methods:
        from_yaml(cls, yaml_path: str): Creates a Bottle instance from a YAML configuration file
    Methods:
        log_pressure(self, time): Logs the current remaining pressure at a given time.
        use_gas(self, amount:int, unit:str="bar", safe:bool=True): Uses a specified amount of gas from the bottle.
    """
    def __init__(self, volume, pressure, type:str="air", ppO2:float=0.21, ppN2:float=0.79,
        reserve:int=50):
        self._volume = volume  
        self._pressure = pressure
        self._remaining_pressure = pressure
        self._type = type
        self._ppO2 = ppO2
        self._ppN2 = ppN2
        self._reserve = reserve
        self._pressure_log = pd.DataFrame(
            columns=["Time", "Remaining Pressure (bar)"],
            data=[[0, self._remaining_pressure]]
        )

##################################################################################################################
## CLASS METHODS
##################################################################################################################

    @classmethod
    def from_yaml(cls, yaml_path: str):
        """
        Create a Bottle instance from a YAML configuration file.
        """
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

#################################################################################################################
## PROPERTIES
#################################################################################################################

    @property
    def volume(self):
        return self._volume
    
    @property
    def pressure(self):
        return self._pressure
    
    @property
    def reserve(self):
        return self._reserve

    @property
    def total_gas_volume(self):
        return self.volume * self.pressure
    
    @property
    def remaining_gas_volume(self):
        return self.volume * self.remaining_pressure
    
    @property
    def remaining_pressure(self):
        return self._remaining_pressure
    
    @property
    def pressure_log(self):
        return self._pressure_log

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

################################################################################################################
## METHODS
################################################################################################################
    
    def log_pressure(self, time):
        """
        Log the current remaining pressure at a given time.

        Parameters:
        - time (float): The time at which to log the remaining pressure.

        Raises:
        - ValueError: If the logged time is not greater than the last logged time
        - ValueError: If the remaining pressure increases over time.
        """
        new_entry = pd.DataFrame([[time, self.remaining_pressure]], columns=["Time", "Remaining Pressure (bar)"])
        if not self._pressure_log.empty and time <= self._pressure_log["Time"].iloc[-1]:
            raise ValueError("Logged time must be greater than the last logged time.")
        if not self._pressure_log.empty and self.remaining_pressure > self._pressure_log["Remaining Pressure (bar)"].iloc[-1]:
            raise ValueError("Remaining pressure cannot increase over time.")
        self._pressure_log = pd.concat([self._pressure_log, new_entry], ignore_index=True)
    
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
        limit_pressure = self.reserve if safe else 0
        pressure_drop = amount if unit == "bar" else amount / self.volume
        if self.remaining_pressure - pressure_drop < limit_pressure:
            raise ValueError(f"Not enough gas remaining in the bottle ({self.remaining_pressure:.2f} bar remaining, {pressure_drop:.2f} bar requested, {limit_pressure:.2f} bar minimum).")
        self.remaining_pressure -= pressure_drop