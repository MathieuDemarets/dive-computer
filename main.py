from dive_computer import DivePlanner, Bottle

# Example usage
surface_consumption = 20  # L/min
depths = [5, 10, 18, 5]
times = [10, 15, 20, 5]
bottle = Bottle(volume=12, pressure=200)

dive_planner = DivePlanner(surface_consumption, depths, times, bottle)

dive_planner.plot_consumption_profile(consumption_unit='L')
dive_planner.plot_consumption_profile(consumption_unit='bar')
