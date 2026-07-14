# Versions

# v0.1.0

Initial release of the dive planner core.

Main features implemented in src/dive_computer:
* Bottle model with total gas calculation (volume x pressure)
* DiveBriefing model to represent a dive profile with:
	* depth and time segments
	* ambient pressure by depth
	* gas consumption by segment and cumulative totals
* Consumption profile export as a pandas DataFrame with:
	* depth, time, pressure, L/min
	* segment consumption in liters and bar
	* cumulative consumption in liters and bar
* Matplotlib plotting utility to visualize:
	* dive profile over time
	* cumulative gas consumption over time
	* max depth and reserve lines

Typical v0.1.0 usage:
```python
from dive_computer import Bottle, DiveBriefing

bottle = Bottle(volume=12, pressure=200)
briefing = DiveBriefing(
		surface_consumption=20,
		depths=[5, 12, 18, 6],
		times=[5, 15, 20, 5],
		bottle=bottle,
		max_depth=18,
)

df = briefing.consumption_profile
briefing.plot_consumption_profile(consumption_unit="bar")
```




# uv instructions

To set up the project, a few simple steps were used:
* uv init dive-computer
* uv sync
* uv add --dev pytest ruff
* uv add pandas numpy matplotlib

Then scripts can be ran with `uv run python <script_name>`. Tools can also be run that way, for example `uv run ruff .` or `uv run pytest`.
