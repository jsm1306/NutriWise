from .models import NutritionInfo
import pulp

def optimize_meal_plan(bmi_category, budget):
    # Get all food items from the database
    food_items = NutritionInfo.objects.all()

    # Define LP Problem
    problem = pulp.LpProblem("Meal_Plan_Optimization", pulp.LpMinimize)

    # Decision Variables: Quantity of each food item to be included
    food_vars = {item.item_name: pulp.LpVariable(f"x_{item.item_name}", lowBound=0, cat="Continuous") for item in food_items}

    # Objective: Minimize Cost
    problem += pulp.lpSum(food_vars[item.item_name] * item.price for item in food_items), "Total_Cost"

    # Constraints: Stay within Budget
    problem += pulp.lpSum(food_vars[item.item_name] * item.price for item in food_items) <= budget, "Budget_Constraint"

    # Constraints: Meet Nutritional Needs
    if bmi_category == "Underweight":
        problem += pulp.lpSum(food_vars[item.item_name] * item.calories for item in food_items) >= 2500, "Calorie_Intake"
    elif bmi_category == "Overweight":
        problem += pulp.lpSum(food_vars[item.item_name] * item.calories for item in food_items) <= 1800, "Calorie_Limit"
    else:
        problem += pulp.lpSum(food_vars[item.item_name] * item.calories for item in food_items) >= 2000, "Calorie_Maintenance"

    # Solve Problem
    problem.solve()

    # Generate Meal Plan
    meal_plan = {}
    for item in food_items:
        if food_vars[item.item_name].varValue > 0:
            meal_plan[item.item_name] = round(food_vars[item.item_name].varValue, 2)

    return meal_plan
