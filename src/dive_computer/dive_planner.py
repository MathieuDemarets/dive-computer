import pandas as pd
import matplotlib.pyplot as plt
import os
# relative imports
from .bottle import Bottle
from .parameters import Parameters

class DivePlanner:
    def __init__(
        self,
        surface_consumption: float,
        safety_stop_depth: int,
        safety_stop_time: int,
        max_depth: int,
        max_ppo2: float,
        bottle: Bottle
    ):
        self._surface_consumption = surface_consumption
        self._safety_stop_depth = safety_stop_depth
        self._safety_stop_time = safety_stop_time
        self._bottle = bottle
        self._max_depth = max_depth
        self._max_ppo2 = max_ppo2
        self._dive_log = pd.DataFrame(
            columns=[
                "Step", "Type", 
                "Start Time (min)", "End Time (min)", 
                "Start Depth (m)", "End Depth (m)", 
                "Start Pressure (bar)", "End Pressure (bar)",
                "Start Remaining Pressure (bar)", "End Remaining Pressure (bar)",
                "Start ppO2 (bar)", "End ppO2 (bar)",
                "Consumption (L)", "Total Consumption (L)",
                "Consumption (bar)", "Total Consumption (bar)"
            ],
            data=[]
        )
        self._parameters = None

##################################################################################################################
## CLASS METHODS
##################################################################################################################

    @classmethod
    def from_yaml(cls, config_file: str, referential_file: str):
        params = Parameters(config_file, referential_file)
        dive_planner = cls(
            surface_consumption=params.get_parameter(["consumption", "surface"]),
            safety_stop_depth=params.get_parameter(["safety", "safetyStop", "depth"]),
            safety_stop_time=params.get_parameter(["safety", "safetyStop", "time"]),
            max_depth=params.get_parameter(["attributes", "certification", "maxDepth"]),
            max_ppo2=params.get_parameter(["attributes", "certification", "maxPpO2"]),
            bottle=Bottle.from_yaml(config_file, referential_file)
        )
        dive_planner._parameters = params
        return dive_planner

##################################################################################################################
## PROPERTIES
##################################################################################################################

    @property
    def surface_consumption(self):
        return self._surface_consumption
    @property
    def safety_stop_depth(self):
        return self._safety_stop_depth
    @property
    def safety_stop_time(self):
        return self._safety_stop_time
    @property
    def max_depth(self):
        return self._max_depth
    @property
    def bottle(self):
        return self._bottle
    @property
    def max_ppo2(self):
        return self._max_ppo2
    @property
    def parameters(self):
        return self._parameters
    @property
    def dive_log(self):
        return self._dive_log
    
    def dive_log_append(self, new_log: pd.DataFrame):
        assert isinstance(new_log, pd.DataFrame), "new_log must be a pandas DataFrame"
        assert all(col in new_log.columns for col in self._dive_log.columns), "new_log must have the same columns as the existing dive log"
        self._dive_log = pd.concat([self._dive_log, new_log], ignore_index=True)

    def dive_log_reset(self):
        self._dive_log = pd.DataFrame(
            columns=[
                "Step", "Type", 
                "Start Time (min)", "End Time (min)", 
                "Start Depth (m)", "End Depth (m)", 
                "Start Pressure (bar)", "End Pressure (bar)",
                "Start Remaining Pressure (bar)", "End Remaining Pressure (bar)",
                "Start ppO2 (bar)", "End ppO2 (bar)",
                "Consumption (L)", "Total Consumption (L)",
                "Consumption (bar)", "Total Consumption (bar)"
            ],
            data=[]
        )

###################################################################################################################
## METHODS
###################################################################################################################

    def pressure_at_depth(self, depth: float) -> float:
        """
        Calculate the pressure at a given depth in bar.
        
        Parameters:
            depth (float): The depth in meters.

        Returns:
            float: The pressure in bar.
        """
        return 1 + (depth / 10)
    
    def ppO2_at_depth(self, depth: float) -> float:
        """
        Calculate the partial pressure of oxygen (ppO2) at a given depth in bar.
        
        Parameters:
            depth (float): The depth in meters.
        
        Returns:
            float: The partial pressure of oxygen in bar.
        """
        pressure = self.pressure_at_depth(depth)
        return pressure * self.parameters.get_parameter(["attributes", "bottle", "type", "ppO2"])
    
    def test_depth_safe(self, depth: float):
        """
        Test if the dive is safe at a given depth.
        
        Parameters:
            depth (float): The depth in meters.

        Raises:
            AssertionError: If the ppO2 at the given depth exceeds the maximum ppO2.
            AssertionError: If the depth exceeds the maximum depth for the certification.
        """
        assert self.ppO2_at_depth(depth) <= self.max_ppo2, f"ppO2 at depth {depth}m ({self.ppO2_at_depth(depth):.2f} bar) exceeds max ppO2 of {self.max_ppo2} bar"
        assert depth <= self.max_depth, f"Depth {depth}m exceeds max depth of {self.max_depth}m (for certification {self.parameters.get_parameter(['certification'])})"
    
    def consumption_level(
            self,
            start_time: int,
            end_time: int,
            start_depth: float,
            end_depth: float,
            unit: str = "L"
        ) -> float:
        """
        Calculate the consumption level at a given depth in liters per minute.
        
        Parameters:
            start_time (int): The start time in minutes.
            end_time (int): The end time in minutes.
            start_depth (float): The start depth in meters.
            end_depth (float): The end depth in meters.
            unit (str): The unit of measurement for consumption ("L" or "bar"). Defaults to "L".
        
        Returns:
            float: The consumption in liters or bar, depending on the unit specified.
        """
        start_pressure = self.pressure_at_depth(start_depth)
        end_pressure = self.pressure_at_depth(end_depth)
        average_pressure = (start_pressure + end_pressure) / 2
        duration = end_time - start_time
        gas_consumed = self.surface_consumption * average_pressure * duration
        if unit == "L":
            return gas_consumed
        elif unit == "bar":
            return gas_consumed / self.bottle.volume
        else:
            raise ValueError("Invalid unit. Please use 'L' or 'bar'.")
    
    def add_dive_step(self, step_type:str, time: int, end_depth: float, warning:bool=True):
        """
        Add a dive step to the dive log.
        
        Parameters:
            step_type (str): The type of the dive step (e.g., "Descent", "Level", "Bottom", "Ascent", "Safety Stop").
            time (int): The time in minutes.
            end_depth (float): The end depth in meters.
            warning (bool): Whether to include a warning for this step. Defaults to True.
        """
        if self.parameters is not None:
            accepted_step_types = self.parameters.get_parameter(["accepted_inputs", "dive_planner", "dive_log", "type"])
            assert step_type in accepted_step_types, f"Invalid step type: {step_type}. Accepted step types: {accepted_step_types}"
        step = len(self._dive_log)
        if step == 0:
            self.dive_log_append(pd.DataFrame([[
                step, "Start", 0, 0, 0, 0, self.pressure_at_depth(0), self.pressure_at_depth(0), self.bottle.pressure, self.bottle.pressure, self.ppO2_at_depth(0), self.ppO2_at_depth(0), 0, 0, 0, 0
            ]],
                columns=self._dive_log.columns
            ))
        start_time = self._dive_log["End Time (min)"].iloc[-1]
        start_depth = self._dive_log["End Depth (m)"].iloc[-1]
        start_remaining_pressure = self._dive_log["End Remaining Pressure (bar)"].iloc[-1]
        start_total_consumption_L = self._dive_log["Total Consumption (L)"].iloc[-1]
        start_total_consumption_bar = self._dive_log["Total Consumption (bar)"].iloc[-1]
        # calculation
        step = len(self._dive_log)
        end_time = start_time + time
        start_pressure = self.pressure_at_depth(start_depth)
        end_pressure = self.pressure_at_depth(end_depth)
        start_ppO2 = self.ppO2_at_depth(start_depth)
        end_ppO2 = self.ppO2_at_depth(end_depth)
        consumption_L = self.consumption_level(start_time, end_time, start_depth, end_depth, unit="L")
        total_consumption_L = start_total_consumption_L + consumption_L
        consumption_bar = self.consumption_level(start_time, end_time, start_depth, end_depth, unit="bar")
        total_consumption_bar = start_total_consumption_bar + consumption_bar

        if warning:
            self.test_depth_safe(end_depth)
            assert start_remaining_pressure - self.bottle.reserve >= consumption_bar, f"Not enough gas for step {step} ({step_type}). Remaining pressure: {start_remaining_pressure:.2f} bar, Consumption: {consumption_bar:.2f} bar, Reserve: {self.bottle.reserve:.2f} bar"

        self.dive_log_append(pd.DataFrame([[
            step, step_type, start_time, end_time, start_depth, end_depth, start_pressure, end_pressure,
            start_remaining_pressure, start_remaining_pressure - consumption_bar,
            start_ppO2, end_ppO2,
            consumption_L, total_consumption_L,
            consumption_bar, total_consumption_bar
            ]],
            columns=self._dive_log.columns
        ))
    
    def add_automatic_transitions(self, dive_steps:list) -> list:
        """
        Add automatic transitions (Ascend/Descend) between dive steps if needed.
        
        Parameters:
            dive_steps (list): A list of tuples containing (step_type, time, end_depth).
        
        Returns:
            list: A new list of dive steps with automatic transitions added.
        """
        transition_time = self.parameters.get_parameter(["transitionTime"])
        final_dive_steps = []
        ascent_to_safety_i = None
        safety_stop_i = None
        ascend_to_surface_i = None
        add_before_end = []
        for i in range(len(dive_steps)):
            if i == 0 and dive_steps[i][0] != "Descent":
                final_dive_steps.append(("Descent", transition_time, dive_steps[i][2]))
                final_dive_steps.append(dive_steps[i])
            elif i >= len(dive_steps) - 3:
                if dive_steps[i][0] == "Ascent" and dive_steps[i][2] == self.safety_stop_depth:
                    ascent_to_safety_i = i
                elif dive_steps[i][0] == "Safety Stop" and dive_steps[i][2] == self.safety_stop_depth:
                    safety_stop_i = i
                elif dive_steps[i][0] == "Ascent" and dive_steps[i][2] == 0:
                    ascend_to_surface_i = i
                else:
                    add_before_end = add_before_end + [i]
            else:
                if dive_steps[i][0] in ("Level", "Bottom") and dive_steps[i][2] < dive_steps[i - 1][2]:
                    final_dive_steps.append(("Ascent", transition_time, dive_steps[i][2]))
                    final_dive_steps.append(dive_steps[i])
                elif dive_steps[i][0] in ("Level", "Bottom") and dive_steps[i][2] > dive_steps[i - 1][2]:
                    final_dive_steps.append(("Descent", transition_time, dive_steps[i][2]))
                    final_dive_steps.append(dive_steps[i])
                else:
                    final_dive_steps.append(dive_steps[i])
        for k in add_before_end:
            if dive_steps[k][0] in ("Level", "Bottom") and dive_steps[k][2] < dive_steps[k - 1][2]:
                final_dive_steps.append(("Ascent", transition_time, dive_steps[k][2]))
                final_dive_steps.append(dive_steps[k])
            elif dive_steps[k][0] in ("Level", "Bottom") and dive_steps[k][2] > dive_steps[k - 1][2]:
                final_dive_steps.append(("Descent", transition_time, dive_steps[k][2]))
                final_dive_steps.append(dive_steps[k])
            else:
                final_dive_steps.append(dive_steps[k])
        final_dive_steps.append(("Ascent", transition_time, self.safety_stop_depth) if ascent_to_safety_i is None else dive_steps[ascent_to_safety_i])
        final_dive_steps.append(("Safety Stop", self.safety_stop_time, self.safety_stop_depth) if safety_stop_i is None else dive_steps[safety_stop_i])
        final_dive_steps.append(("Ascent", transition_time, 0) if ascend_to_surface_i is None else dive_steps[ascend_to_surface_i])
        return final_dive_steps

    def make_dive_plan(self, dive_steps:list, automatic_transitions:bool=True, excel:str=None) -> str:
        """
        Make a dive plan based on a list of dive steps.
        
        Parameters:
            dive_steps (list): A list of tuples containing (step_type, time, end_depth).
            automatic_transitions (bool): Whether to automatically add Ascend/Descend steps between dive steps. Defaults to True.
        
        Returns:
            str: A message indicating whether the dive plan is valid or not.
        """
        if not self.dive_log.empty:
            self.dive_log_reset()

        # Add automatic transitions if enabled
        final_dive_steps = self.add_automatic_transitions(dive_steps) if automatic_transitions else dive_steps

        for (step_type, time, end_depth) in final_dive_steps:
            try:
                self.add_dive_step(step_type, time, end_depth)
            except AssertionError as e:
                self.dive_log_reset()
                return f"The dive plan is invalid ({e})."
        if excel is not None:
            if not os.path.exists(os.path.dirname(excel)):
                os.makedirs(os.path.dirname(excel))
            self.dive_log.to_excel(excel, index=False)
        return "The dive plan is valid (see dive log for details)."
    
# Visualization

    def visualize_dive_plan(self, save_path:str=None):
        """
        Plot the dive log showing depth over time and remaining pressure over time.
        """
        if self.dive_log.empty:
            print("Dive log is empty. No data to plot.")
            return
        
        # Two plots, one above, the other below, sharing the same x-axis (time)
        fig, (ax1, ax2) = plt.subplots(figsize=(8, 6), nrows=2, ncols=1, sharex=True)

        for i in range(len(self.dive_log)):
            ax1.plot(
                [self.dive_log["Start Time (min)"].iloc[i], self.dive_log["End Time (min)"].iloc[i]],
                [-self.dive_log["Start Depth (m)"].iloc[i], -self.dive_log["End Depth (m)"].iloc[i]],
                color='blue', linewidth=2
            )
            ax2.plot(
                [self.dive_log["Start Time (min)"].iloc[i], self.dive_log["End Time (min)"].iloc[i]],
                [self.dive_log["Start Remaining Pressure (bar)"].iloc[i], self.dive_log["End Remaining Pressure (bar)"].iloc[i]],
                color='green', linewidth=2
            )
        ax2.axhline(y=self.bottle.reserve, color='purple', linestyle='--', label='Reserve Pressure')
        ax2.axhline(y=self.bottle.pressure, color='black', linestyle='--', label='Full Pressure')
        ax1.axhline(y=-self.safety_stop_depth, color='orange', linestyle='--', label='Safety Stop Depth')
        ax1.axhline(y=-self.max_depth, color='red', linestyle='--', label='Max Depth')
        
        ax1.set_ylabel("Depth (m)", color="blue")
        ax1.tick_params(axis='y', labelcolor="blue")
        ax1.set_ylim(-(self.max_depth + 5), 0)
        ax1.legend(loc='lower right')
        ax1.grid()

        ax2.set_xlabel("Time (min)")
        ax2.set_ylabel("Remaining Pressure (bar)", color="green")
        ax2.tick_params(axis='y', labelcolor="green", )
        ax2.set_ylim(0, self.bottle.pressure + 10)
        ax2.set_yticks(range(0, int(self.bottle.pressure) + 26, 25))
        ax2.legend(loc='upper right')
        ax2.grid()

        # for the x-axis, set the ticks to be the start and end times of each step in the dive log
        ax2.set_xticks(list(set(self.dive_log["Start Time (min)"].tolist() + self.dive_log["End Time (min)"].tolist())))

        fig.suptitle("Dive Plan Visualization", fontsize=16)
        ax1.set_title("Dive Depth Profile", fontsize=14)
        ax2.set_title("Remaining Tank Pressure Profile", fontsize=14)
        fig.tight_layout()
        if save_path:
            if not os.path.exists(os.path.dirname(save_path)):
                os.makedirs(os.path.dirname(save_path))
            plt.savefig(save_path)
            plt.show()
        else:
            plt.show()