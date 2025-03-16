from .models import *

DAILY_REQUIREMENTS = {
    'Female': {
        (4, 8):  {'Calories': 1200, 'Proteins': 19, 'Fats': 70, 'Sodium': 2300, 'Fiber': 25, 'Carbs': 260, 'Sugar': 50},
        (9, 13): {'Calories': 1600, 'Proteins': 34, 'Fats': 70, 'Sodium': 2300, 'Fiber': 26, 'Carbs': 290, 'Sugar': 50},
        (14, 18): {'Calories': 1800, 'Proteins': 46, 'Fats': 70, 'Sodium': 2300, 'Fiber': 26, 'Carbs': 300, 'Sugar': 50},
        (19, 30): {'Calories': 2000, 'Proteins': 46, 'Fats': 70, 'Sodium': 2300, 'Fiber': 28, 'Carbs': 310, 'Sugar': 50},
        (31, 50): {'Calories': 1800, 'Proteins': 46, 'Fats': 70, 'Sodium': 2300, 'Fiber': 28, 'Carbs': 300, 'Sugar': 50},
        (51, 70): {'Calories': 1600, 'Proteins': 46, 'Fats': 70, 'Sodium': 2300, 'Fiber': 28, 'Carbs': 260, 'Sugar': 50},
        (71, 100): {'Calories': 1500, 'Proteins': 46, 'Fats': 70, 'Sodium': 2300, 'Fiber': 28, 'Carbs': 250, 'Sugar': 50},
    },
    'Male': {
        (4, 8):  {'Calories': 1400, 'Proteins': 19, 'Fats': 70, 'Sodium': 2300, 'Fiber': 25, 'Carbs': 270, 'Sugar': 50},
        (9, 13): {'Calories': 1800, 'Proteins': 34, 'Fats': 70, 'Sodium': 2300, 'Fiber': 31, 'Carbs': 300, 'Sugar': 50},
        (14, 18): {'Calories': 2200, 'Proteins': 52, 'Fats': 70, 'Sodium': 2300, 'Fiber': 31, 'Carbs': 320, 'Sugar': 50},
        (19, 30): {'Calories': 2400, 'Proteins': 56, 'Fats': 70, 'Sodium': 2300, 'Fiber': 34, 'Carbs': 330, 'Sugar': 50},
        (31, 50): {'Calories': 2200, 'Proteins': 56, 'Fats': 70, 'Sodium': 2300, 'Fiber': 34, 'Carbs': 300, 'Sugar': 50},
        (51, 70): {'Calories': 2000, 'Proteins': 56, 'Fats': 70, 'Sodium': 2300, 'Fiber': 30, 'Carbs': 280, 'Sugar': 50},
        (71, 100): {'Calories': 1800, 'Proteins': 56, 'Fats': 70, 'Sodium': 2300, 'Fiber': 30, 'Carbs': 250, 'Sugar': 50},
    }
}

def get_daily_requirements(age, gender):
    """Returns the daily nutritional requirements based on age and gender."""
    for age_range, requirements in DAILY_REQUIREMENTS.get(gender, {}).items():
        if age_range[0] <= age <= age_range[1]:
            return requirements
    return {}

def load_nutrition_data():
    """Loads nutrition data from the database and returns it as a dictionary."""
    nutrition_data = {}
    nutrition_items = NutritionInfo.objects.all()
    
    for item in nutrition_items:
        nutrition_data[item.item_name.lower()] = {
            'Calories': item.calories,
            'Proteins': item.proteins,
            'Fats': item.fats,
            'Sodium': item.sodium,
            'Fiber': item.fiber,
            'Carbs': item.carbs,
            'Sugar': item.sugar,
            'UnitWeight': item.unit_weight
        }
    return nutrition_data
