from django.urls import path
from . import views
urlpatterns=[
    path('bmicalc',views.bmicalc,name='bmicalc'),
    path('', views.score, name='score'), 
    path('compute/', views.compute, name='compute'),
    path('category-wise-items/', views.category_wise_items, name='category-wise-items'),
    # path('dropdown/', views.dropdown, name='dropdown'),
    path('categorize/', views.categorize, name='categorize'),
    path('suggester/', views.suggester, name='suggester'),
    # path('chart/', views.viewgraphs, name='viewgraphs'),
    # path('categoryback',views.categoriesbackbtn, name='categoryback'),
    path('categorize/', views.categorize, name='categorize'),
    path('register/',views.registerPage,name='register'),
    path('login/',views.loginPage,name='login'),
    path('logout/',views.logoutPage,name='logout'),
    path('user-history/', views.user_history, name='user_history'),
    path('moreinfo/',views.moreinfo,name='moreinfo'), 
    path('mealplan/', views.meal_plan, name='mealplan'),
    path('finalize-meal-plan/', views.finalize_meal_plan, name='finalize_meal_plan'),
    path('finalize-meal-plan/pdf/', views.finalize_meal_plan_pdf, name='finalize_meal_plan_pdf'),

]