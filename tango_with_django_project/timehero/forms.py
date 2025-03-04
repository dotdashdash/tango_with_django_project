from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(required=True)
    SECURITY_QUESTIONS = [
        ('你的第一只宠物叫什么名字？', '你的第一只宠物叫什么名字？'),
        ('你母亲的名字是什么？', '你母亲的名字是什么？'),
        ('你出生的城市是哪里？', '你出生的城市是哪里？'),
    ]
    security_question = forms.ChoiceField(choices=SECURITY_QUESTIONS, required=True, label="安全问题")
    security_answer = forms.CharField(max_length=255, required=True, label="安全答案")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'security_question', 'security_answer']

class UserLoginForm(AuthenticationForm):
    """用户登录表单"""
    username = forms.CharField(label="用户名", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
