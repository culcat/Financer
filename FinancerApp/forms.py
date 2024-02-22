from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from FinancerApp.models import *

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'category']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category']