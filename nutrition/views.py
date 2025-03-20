from django.shortcuts import render, redirect
from django.urls import reverse
import requests
from django.conf import settings
from .models import *
from scipy.optimize import linprog
import numpy as np
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control 
import random
from django.shortcuts import get_object_or_404

def registerPage(request):
        form=UserCreationForm()
        if request.method=="POST":
            form=UserCreationForm(request.POST)
            if form.is_valid():
                user=form.save()
                UserProfile.objects.create(user=user)

                return redirect('login')
            else:
                messages.error(request,"Password does not follow the rules")
        context={'form':form}
        return render(request, 'register.html', context)
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('mains')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['username'] = username
                
                return redirect('mains')
            else:
                messages.success(request, "Username or Password is incorrect")
    return render(request, 'login.html')


@login_required(login_url='login')
def logoutPage(request):
    logout(request)
    return redirect('login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def mains(request):#dummy
    return render(request,'mains.html',{'result':'Diet Score'})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def category_wise_items(request):#to display categories in category.html(navbar)
    categories = Category.objects.all()
    items_by_category = {category.name: NutritionInfo.objects.filter(category=category) for category in categories}
    
    context = {
        'items_by_category': items_by_category
    }
    return render(request, 'categorylist.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def add(request):
    if request.method == 'POST':
        username = request.session.get('username')
        if username:
            age=int(request.POST['age'])
            gender=request.POST.get('options', '')
            request.session['age'] = age
            request.session['gender'] = gender
            request.session['name'] = username
            user = User.objects.filter(username=username).first()
            if user:
                user_profile, created = UserProfile.objects.get_or_create(user=user)
                user_profile.age = age
                user_profile.gender = gender
                user_profile.save()

            nutrition_items = NutritionInfo.objects.all()

            return render(request, 'score.html', {
                'age': age,
                'name': username,
                'gender': gender,
                'nutrition_items': nutrition_items,
            })
    return render(request, 'mains.html')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def categorize(request):#to display items category wise
    items_by_category = {}
    categories = Category.objects.all()  
    for category in categories:
        items = NutritionInfo.objects.filter(category=category)  
        items_by_category[category.name] = items 
    context = {
        'items_by_category': items_by_category
    }
    return render(request, 'selectcategories.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def suggester(request):
    if request.method == "POST":
        latest = UserSubmission.objects.filter(user=request.user).prefetch_related('items').order_by('-submitted_at').first()
        selected_items = []
        for category, items in request.POST.items():
            if category.startswith('item_'):
                selected_items.append(items)  

        nutrition_data = []
        for item_name in selected_items:
            try:
                item = NutritionInfo.objects.get(item_name=item_name)
                nutrition_data.append(item)
            except NutritionInfo.DoesNotExist:
                print(f"Item '{item_name}' does not exist in the database.")
        requirements = daily(request)
        A = [
            [-item.calories for item in nutrition_data],
            [-item.proteins for item in nutrition_data],
            [-item.fats for item in nutrition_data],
            [-item.sodium for item in nutrition_data],
            [-item.fiber for item in nutrition_data],
            [-item.carbs for item in nutrition_data],
            [-item.sugar for item in nutrition_data]
        ]

        b = [-requirements['Calories'], -requirements['Proteins'], -requirements['Fats'],
             -requirements['Sodium'], -requirements['Fiber'], -requirements['Carbs'], -requirements['Sugar']]
        c = [item.price for item in nutrition_data]
        x_bounds = [(0, None) for _ in nutrition_data]

        res = linprog(c, A_ub=A, b_ub=b, bounds=x_bounds, options={"disp": True})

        quantities = res.x 
        
 
        results = [(item, quantity,item.price) for item, quantity in zip(nutrition_data, quantities)]

        return render(request, 'suggestresult.html', {'results': results, 'latestsub': latest})

    return redirect('mains.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def score(request):#back button fn in inputsbase.html
    name = request.session.get('name')  
    age = request.session.get('age')    
    username = request.session.get('username') 
    # print(name, age, username)
    nutrition_items = NutritionInfo.objects.values_list('item_name', flat=True)
    return render(request, 'score.html', {
        'name': name,
        'age': age,
        'username': username,
        'nutrition_items': nutrition_items,
    })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def bmicalc(request):
    if request.method == "POST":
        weight = int(request.POST.get('weig', 0))
        height = int(request.POST.get('heig', 0))
        age = int(request.POST.get('age', 0))
        gender = request.POST.get('options', '')

        if height <= 0 or weight <= 0:
            return render(request, 'bmiresult.html', {'error': "Height/Weight should be positive numbers.", 'age': age, 'gender': gender})
        if age < 0 or age > 100:
            return render(request, 'bmiresult.html', {'error': "Invalid age.", 'age': age, 'gender': gender})

        bmi_value = weight / ((height / 100) ** 2)

        if bmi_value < 18.5:
            category = "Underweight"
        elif 18.5 <= bmi_value < 25:
            category = "Normal weight"
        elif 25 <= bmi_value < 29.9:
            category = "Overweight"
        else:
            category = "Obese"

        BMICalculation.objects.create(weight=weight, height=height, bmi_value=bmi_value, gender=gender, category=category)

        return render(request, 'bmiresult.html', {'result': round(bmi_value, 2), 'age': age, 'gender': gender, 'category': category})

    return render(request, 'bmical.html')
@login_required(login_url='login')
def daily(request):#this fn is to determine the min requirements based on age&gender, use in compute fn
    age = request.session.get('age')
    gender = request.session.get('gender')
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
    for age_range, requirements in DAILY_REQUIREMENTS.get(gender, {}).items():
        if age_range[0] <= age <= age_range[1]:
            return requirements
    return {} 

def load_nutrition_data():# this fn is to load the nutrition data of items and use in compute fn
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

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def compute(request):#**** fn, to calculate req met or not, sum divide and compare
    if request.method == 'POST':
        items = request.POST.getlist('item[]')
        quantities = request.POST.getlist('quantity[]')
        nutrition_data = load_nutrition_data()
        requirements = daily(request)

        item_quantities = [(item.lower().strip(), quantity) for item, quantity in zip(items, quantities)]
        request.session['item_quantities'] = item_quantities

        if not requirements:
            print("Error1-not found")
            requirements = {'Calories': 0, 'Proteins': 0, 'Fats': 0, 'Sodium': 0, 'Fiber': 0, 'Carbs': 0, 'Sugar': 0}
        totals = {'Calories': 0, 'Proteins': 0, 'Fats': 0, 'Sodium': 0, 'Fiber': 0, 'Carbs': 0, 'Sugar': 0}
        item_details = []
        submission = UserSubmission.objects.create(user=request.user)
        for item, quantity in zip(items, quantities):
            item = item.lower().strip()
            try:
                quantity = int(quantity)
                if item in nutrition_data:
                    item_info = nutrition_data[item]
                    unit_weight = item_info['UnitWeight']
                    total_weight = quantity * unit_weight
                    for key in totals:
                        totals[key] += (item_info[key] * total_weight / 100)
                        totals[key] = round(totals[key], 2)
                    item_details.append((item, total_weight, item_info))
                    ItemEntry.objects.create(#to edit items entered by user in database
                        submission=submission,
                        item_name=item,
                        quantity=total_weight,
                        calories=item_info['Calories']*total_weight/100,
                        proteins=item_info['Proteins']*total_weight/100,
                        fats=item_info['Fats']*total_weight/100,
                        sodium=item_info['Sodium']*total_weight/100,
                        fiber=item_info['Fiber']*total_weight/100,
                        carbs=item_info['Carbs']*total_weight/100,
                        sugar=item_info['Sugar']*total_weight/100
                    )
            except ValueError:
                print("Error2-cant fetch")#print in console
         #comparing calculated nutrition with min req
        meets_requirements = {key: totals[key] >= requirements[key] for key in totals}
        request.session['totals'] = totals
        context = {
            'item_details': item_details,
            'totals': totals,
            'meets_requirements': meets_requirements,
            'requirement': requirements
        }
        return render(request,'inputsbase.html',context)

    return render(request,'score.html')
'''
Changes to be made: 
● Stylize few things
● add a pop up button in inputsbase.html stating you have not met these requirements
● Should update unitweight of each item
● check buttons
'''
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def suggester_view(request):
    if request.method == 'POST':
        selected_items = []
        for category in request.POST:
            if category.startswith('item_'):
                selected_item_name = request.POST[category]
                if selected_item_name:
                    item = NutritionInfo.objects.get(item_name=selected_item_name)
                    selected_items.append(item)

        return render(request, 'suggestresult.html', {'results': selected_items})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def user_history(request):
    user_submissions = UserSubmission.objects.filter(user=request.user).prefetch_related('items').order_by('-submitted_at')
    
    context = {
        'submissions': user_submissions,
    }
    return render(request, 'user_history.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def moreinfo(request):
    return render(request,'optimzerinfo.html')

def meal_plan(request):
    categories = {cat.name.lower(): cat for cat in Category.objects.all()}
    meal_categories = {
        'morning': NutritionInfo.objects.filter(category=categories.get("tiffin")),
        'afternoon': NutritionInfo.objects.all(),
        'evening': NutritionInfo.objects.filter(category=categories.get("snacks")),
        'night': NutritionInfo.objects.all()
    }
    days = list(range(1, 8))
    current_day = int(request.GET.get('day', 1))
    if 'selected_items' not in request.session:
        request.session['selected_items'] = {day: {'morning': [], 'afternoon': [], 'evening': [], 'night': []} for day in days}
    selected_items = request.session['selected_items']
    notification = ""
    if request.method == "POST":
        selected_day = int(request.POST.get("day", current_day))
        selected_items[selected_day] = {
            'morning': request.POST.getlist("morning[]"),
            'afternoon': request.POST.getlist("afternoon[]"),
            'evening': request.POST.getlist("evening[]"),   
            'night': request.POST.getlist("night[]"),
        }
        request.session['selected_items'] = selected_items
        optimized_plan, validation_result = optimize_and_validate(request,selected_items[selected_day])
        if validation_result == "Yes":
            notification = "Meal validated and optimized successfully!"
            if selected_day == 7:
                return redirect(reverse('finalize_meal_plan'))
            next_day = min(selected_day + 1, 7)
            return redirect(f"{reverse('mealplan')}?day={next_day}")
        else:
            notification = "Meal validation failed. Please adjust your meal plan."
    return render(request, 'mealplan.html', {
        'days': days,
        'current_day': current_day,
        'meal_categories': meal_categories,
        'selected_items': selected_items.get(current_day, {}),
        'tiffins': meal_categories['morning'],
        'snacks': meal_categories['evening'],
        'notification': notification,
        'all_items': NutritionInfo.objects.all(),
    })
def daily_nutrition_requirements(age, gender):
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

    for age_range, requirements in DAILY_REQUIREMENTS.get(gender, {}).items():
        if age_range[0] <= age <= age_range[1]:
            return requirements
    return {}  

def optimize_and_validate(request,selected_items):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    age = user_profile.age
    gender = user_profile.gender

    required_nutrition = daily_nutrition_requirements(age, gender)
    total_nutrition = {key: 0 for key in required_nutrition}
    food_items = []
    healthy_items = []
    unhealthy_items = []
    A = []
    cost = []
    bounds = []

    for meal, items in selected_items.items():
        for item_name in items:
            try:
                food = NutritionInfo.objects.get(item_name=item_name)
                food_items.append(item_name)
                A.append([
                    food.calories, food.proteins, food.fats, food.sodium, 
                    food.fiber, food.carbs, food.sugar
                ])
                cost.append(food.price)

                if food.healthy:
                    healthy_items.append(item_name)
                    bounds.append((2, 10))  
                else:
                    unhealthy_items.append(item_name)
                    bounds.append((1, 3))  
            except NutritionInfo.DoesNotExist:
                print(f"Item '{item_name}' not found in NutritionInfo table.")

    print(f"Selected Food Items: {food_items}")
    print(f"Healthy: {len(healthy_items)}, Unhealthy: {len(unhealthy_items)}")

    total_items = len(food_items)
    if total_items == 0:
        print("Validation failed: No items selected.")
        return [], "No"

    min_healthy = int(0.7 * total_items)
    max_unhealthy = total_items - min_healthy
    if len(healthy_items) < min_healthy or len(unhealthy_items) > max_unhealthy:
        print("Validation failed: Unhealthy/healthy balance not met.")
        return [], "No"

    A = np.array(A).T  

    if A.shape[1] == 0:
        print("Validation failed: No valid nutrition data.")
        return [], "No"

    print("A matrix:", A)
    print("Cost:", cost)
    print("Required nutrition:", required_nutrition)

    try:
        res = linprog(
            c=cost, 
            A_ub=-A,  
            b_ub=-np.array(list(required_nutrition.values())),  
            bounds=bounds,
            method="highs"
        )

        print(f"Optimization success: {res.success}, Message: {res.message}")
        print(f"Optimized meal plan: {res.x}")

        if not res.success:
            print("Optimization failed. Detailed results:")
            print(f"Status: {res.status}")
            print(f"Fun: {res.fun}")
            print(f"X: {res.x}")
            print(f"Slack: {res.slack}")
            print(f"Con: {res.con}")
            print(f"Message: {res.message}")

        if res.success:
            optimized_quantities= [x*100 for x in res.x]
            return list(zip(food_items, optimized_quantities)), "Yes"
        else:
            return [], "No"

    except Exception as e:
        print(f"Error in optimization: {e}")
        return [], "No"


def finalize_meal_plan(request):
    user_meal_plan = request.session.get('selected_items', {})
    optimized_meal_plan = {}

    for day, meals in user_meal_plan.items():
        optimized_meal_plan[day] = {}
        for meal_time, items in meals.items():
            optimized_items, validation_result = optimize_and_validate(request, {meal_time: items})
            optimized_meal_plan[day][meal_time] = optimized_items

    return render(request, 'newhtml.html', {
        'user_meal_plan': user_meal_plan,
        'optimized_meal_plan': optimized_meal_plan
    })
'''
Changes to be made:
● Should add more items to database
● Should render the quantity
● Should also add a constraint to add min of 6 items in a day
● Should plan to add constraint week wise
● maybe fix ui lollll
'''