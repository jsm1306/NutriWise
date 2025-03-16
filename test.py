from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpBinary

# Define food items with their cost, calories, protein, and fat
food_data = {
    "banana": {"cost": 10, "calories": 89, "protein": 1.1, "fat": 0.3},
    "masala_dosa": {"cost": 50, "calories": 250, "protein": 4, "fat": 10},
    "gulab_jamun": {"cost": 40, "calories": 150, "protein": 2, "fat": 5},
    "pistachio": {"cost": 70, "calories": 160, "protein": 6, "fat": 13},
    "curd": {"cost": 20, "calories": 98, "protein": 11, "fat": 3},
    "lays": {"cost": 30, "calories": 150, "protein": 2, "fat": 10},
    "paneer_butter_masala": {"cost": 120, "calories": 300, "protein": 15, "fat": 20},
    "chicken_biryani": {"cost": 150, "calories": 400, "protein": 20, "fat": 15},
    "vegetable_curry": {"cost": 80, "calories": 200, "protein": 5, "fat": 8},
    "roti": {"cost": 10, "calories": 70, "protein": 2, "fat": 1},
    "rice": {"cost": 20, "calories": 130, "protein": 3, "fat": 0.5},
    "sambar": {"cost": 50, "calories": 150, "protein": 7, "fat": 4},
}

days = range(1, 8)  # 7 days
meals = ["morning", "afternoon", "night"]  # 3 meals per day

# Define the model
model = LpProblem("MealPlan", LpMinimize)

# Decision variables: x[item, day, meal] (binary: 1 if chosen, 0 otherwise)
x = {(item, day, meal): LpVariable(f"x_{item}_{day}_{meal}", cat=LpBinary)
     for item in food_data for day in days for meal in meals}

# Objective: Minimize total cost
model += lpSum(food_data[item]["cost"] * x[item, day, meal] for item in food_data for day in days for meal in meals)

# Constraints: Ensure exactly one food per meal
for day in days:
    for meal in meals:
        model += lpSum(x[item, day, meal] for item in food_data) == 1

# Constraints: Ensure minimum daily nutrition requirements
for day in days:
    model += lpSum(food_data[item]["calories"] * x[item, day, meal] for item in food_data for meal in meals) >= 1800
    model += lpSum(food_data[item]["protein"] * x[item, day, meal] for item in food_data for meal in meals) >= 50
    model += lpSum(food_data[item]["fat"] * x[item, day, meal] for item in food_data for meal in meals) >= 40

# Solve the problem
model.solve()

# Print the meal plan
print("\n📅 7-Day Meal Plan (Minimized Cost) 🍽️\n")
for day in days:
    print(f"🗓️ Day {day}:")
    for meal in meals:
        chosen_food = [item for item in food_data if x[item, day, meal].varValue == 1]
        print(f"  🍽️ {meal.capitalize()}: {chosen_food[0] if chosen_food else 'None'}")
    print()
