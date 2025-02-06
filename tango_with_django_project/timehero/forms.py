from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    """用户登录表单"""
    username = forms.CharField(label="用户名", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
