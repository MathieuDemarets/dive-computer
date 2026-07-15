# Versions

# v0.1.0

Initial release of the dive_computer.

* Bottle model with total gas calculation (volume x pressure)
* DiveBriefing model to represent a dive profile with:
	* depth and time segments
	* ambient pressure by depth
	* gas consumption by segment and cumulative totals
* Consumption profile as a pandas DataFrame with:
	* depth, time, pressure, L/min
	* segment consumption in liters and bar
	* cumulative consumption in liters and bar
* Matplotlib plotting utility to visualize:
	* dive profile over time
	* cumulative gas consumption over time
	* max depth and reserve lines

# v0.1.1

Updates:
* Plot remaining bars instead of consumption bars
* Refactorisation
* Addition of transition time between depths
* Parametrization file
* Security buffers for gas consumption calculations
* Multiple graphs for clarity


# uv instructions

To set up the project, a few simple steps were used:
* uv init dive-computer
* uv sync
* uv add --dev pytest ruff
* uv add pandas numpy matplotlib

Then scripts can be ran with `uv run python <script_name>`. Tools can also be run that way, for example `uv run ruff .` or `uv run pytest`.
