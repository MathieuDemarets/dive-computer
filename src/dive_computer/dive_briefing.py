import pandas as pd
import matplotlib.pyplot as plt
from .bottle import Bottle

class DiveBriefing:
    def __init__(self, surface_consumption, depths, times, bottle: Bottle = Bottle(12, 200), max_depth:int = 18):
        self.surface_consumption = surface_consumption
        self.depths = depths
        self.times = times
        self.bottle = bottle
        self.max_depth = max_depth

    @property
    def bottom(self):
        return max(self.depths)
    
    @property
    def pressure_at_depth(self):
        return [1 + (depth / 10) for depth in self.depths]
    
    @property
    def consumption_at_depth(self):
        consumption = [self.surface_consumption * p for p in self.pressure_at_depth]
        return consumption
    
    @property
    def consumption_profile(self):
        return pd.DataFrame({
            'Depth (m)': self.depths,
            'Time (min)': self.times,
            'Pressure (bar)': self.pressure_at_depth,
            'Consumption (L/min)': self.consumption_at_depth,
            'Consumption (L)': [c * t for c, t in zip(self.consumption_at_depth, self.times)],
            'Total Consumption (L)': pd.Series([c * t for c, t in zip(self.consumption_at_depth, self.times)]).cumsum(),
            "Consumption (bar)": [c * t / self.bottle.volume for c, t in zip(self.consumption_at_depth, self.times)],
            "Total Consumption (bar)": pd.Series([c * t / self.bottle.volume for c, t in zip(self.consumption_at_depth, self.times)]).cumsum()
        })
    
    def plot_consumption_profile(self, consumption_unit: str = 'L'):
        """
        Plots the dive profile and total consumption over time.
        Args:
            consumption_unit (str): The unit of consumption to plot ('L' for liters or 'bar' for bar).
        """
        df = self.consumption_profile
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twinx()

        t = 0
        d = 0
        c = 0

        ax1.set_ylim(-self.max_depth*(1.1), 0)
        ax1.axhline(y=-self.max_depth, color='red', linestyle=':', label='Max Depth')

        if consumption_unit == 'L':
            ax2.set_ylim(0, self.bottle.total_gas * 1.1)
            ax2.axhline(y=self.bottle.total_gas, color='green', linestyle=':', label='Total Bottle Volume (L)')
            ax2.axhline(y=self.bottle.total_gas - self.bottle.volume * 50, color='purple', linestyle=':', label='Reserve (50 bar)')
        elif consumption_unit == 'bar':
            ax2.set_ylim(0, self.bottle.pressure * 1.1)
            ax2.axhline(y=self.bottle.pressure, color='green', linestyle=':', label='Total Bottle Pressure (bar)')
            ax2.axhline(y=self.bottle.pressure - 50, color='purple', linestyle=':', label='Reserve (50 bar)')

        for i in range(len(df)):
            depth = df['Depth (m)'][i]
            duration = df['Time (min)'][i]
            if consumption_unit == 'L':
                cons = df['Total Consumption (L)'][i]
            elif consumption_unit == 'bar':
                cons = df['Total Consumption (bar)'][i]
            else:
                raise ValueError("Invalid consumption unit. Choose 'L' or 'bar'.")

            ax1.plot([t, t], [d, -depth], color='blue')
            ax1.plot([t, t + duration], [-depth, -depth], color='blue')
            ax2.plot([t, t + duration], [c, cons], color='orange', linestyle='--')

            t += duration
            d = -depth
            c = cons

        ax1.set_xlabel('Time (min)')
        ax1.set_ylabel('Depth (m)', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        if consumption_unit == 'L':
            ax2.set_ylabel('Total Consumption (L)', color='orange')
        elif consumption_unit == 'bar':
            ax2.set_ylabel('Total Consumption (bar)', color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')

        fig.suptitle('Dive Profile and Total Consumption')
        fig.legend(loc='upper right', bbox_to_anchor=(1, 1))
        fig.tight_layout()
        plt.show()
    
