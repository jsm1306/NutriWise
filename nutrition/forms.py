# nutrition/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    age = forms.IntegerField(required=True)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], required=True)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'age', 'gender')