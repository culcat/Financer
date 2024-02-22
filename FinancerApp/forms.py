from django.contrib.auth.forms import UserCreationForm
from django.forms import forms

from FinancerApp.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

