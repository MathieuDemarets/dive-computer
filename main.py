from dive_computer import DivePlanner

parameters_file = "./conf/dive_parameters.yml"
referential_file = "./conf/referential.yml"

dive_planner = DivePlanner.from_yaml(parameters_file, referential_file)
steps = []
print("""
Dive Plan Creation:

To check the safety of a dive, you can enter a series of steps in the format: type, duration, depth.
- type: Descent, Level, Bottom, Ascent, Safety Stop
- duration: duration of the step in minutes (integer)
- depth: depth of the step in meters (integer)

For example, to create a dive plan with a descent to 10m for 2 minutes, followed by a level at 10m for 15 minutes, you would enter:
- Descent, 2, 10
- Level, 15, 10
The tool will automatically add the necessary transitions between steps to ensure a safe dive profile.

The tool will first check if the plan is safe and then display the dive plan with automatic transitions added. 
You can enter as many steps as you like, and when you're done, type 'done' to finish the input.
--------------------------
""")
while True:
    step = input("Enter a dive step (type, duration, depth) or 'done' to finish: ")
    if step.lower() == 'done':
        break
    else:
        step_parts = step.split(",")
        if len(step_parts) == 3:
            step_type = step_parts[0].strip()
            duration = int(step_parts[1].strip())
            depth = int(step_parts[2].strip())
            steps.append((step_type, duration, depth))

print("Dive Plan (with automatic transitions):")
print(dive_planner.make_dive_plan(steps, automatic_transitions=True, excel="./exploration/excels/dive_plan.xlsx"))
if not dive_planner.dive_log.empty:
    dive_planner.visualize_dive_plan("./exploration/images/dive_plan.png")
