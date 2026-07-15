# Versions

# v0.1.0

Initial release of the dive_computer.

* Bottle model with total gas calculation (volume x pressure)
* DivePlanner model to represent a dive profile with:
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
* Reworked plotting to show **remaining tank pressure (bar)** over time instead of consumed bar
* Added explicit **transition segments between depth changes** to better model non-instant descents/ascents
* Introduced a **central parameter/config file** to tune dive, tank, and safety assumptions
* Split visualization into **multiple focused charts** for improved readability (profile vs gas evolution)
* Internal **refactoring/cleanup** of planner and plotting code for maintainability
* Added **dive planner** to check the safety of a dive profile against tank capacity and depth/time constraints.

# v0.1.2

Updates:
* Work on documentation and README
* Basic unit tests
* Start of a dash interface for the dive planner to be hosted as a web app


# uv instructions

To set up the project, a few simple steps were used:
* uv init dive-computer
* uv sync
* uv add --dev pytest ruff
* uv add pandas numpy matplotlib

Then scripts can be ran with `uv run python <script_name>`. Tools can also be run that way, for example `uv run ruff .` or `uv run pytest`.
