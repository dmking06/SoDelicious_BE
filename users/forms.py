from django import forms
from django.contrib.auth import get_user_model
from users.admin import UserCreationForm
from django.forms import ModelForm

from users.models import Profile

User = get_user_model()


class RegisterForm(UserCreationForm):
    """
    User registration form. Used with register view and template
    """
    # id templates for css customization
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']


class LoginForm(forms.Form):
    """
    User login form. Used with login view and template
    """
    email = forms.EmailField(label='Email', max_length=100,
                             widget=forms.TextInput(attrs={'autofocus': 'True'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class ProfileForm(forms.Form):
    """
    Profile form. Used with user_info view and template
    """
    email = forms.EmailField(label='Email', max_length=100,
                             widget=forms.TextInput(attrs={'autofocus': 'True'}))

    full_name = forms.CharField(label='Full Name', max_length=100, required=False)
