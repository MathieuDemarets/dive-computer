from dive_computer import DiveBriefing, Bottle

# Example usage
surface_consumption = 20  # L/min
depths = [5, 10, 18, 5]
times = [10, 15, 20, 5]
bottle = Bottle(volume=12, pressure=200)

dive_briefing = DiveBriefing(surface_consumption, depths, times, bottle)

dive_briefing.plot_consumption_profile(consumption_unit='L')
dive_briefing.plot_consumption_profile(consumption_unit='bar')
