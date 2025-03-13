from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(required=True)

    # class Meta:
    #     model = User
    #     fields = ['username', 'email', 'password1', 'password2']
    SECURITY_QUESTIONS = [
        ('What is the name of your first pet？', 'What is the name of your first pet？'),
        ('What is the name of your mom？', 'What is the name of your mom？'),
        ('What is the name of the city that you are born in', 'What is the name of the city that you are born in？'),
    ]
    security_question = forms.ChoiceField(choices=SECURITY_QUESTIONS, required=True, label="Security Question")
    security_answer = forms.CharField(max_length=255, required=True, label="Answer")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'security_question', 'security_answer']


class UserLoginForm(AuthenticationForm):
    """用户登录表单"""
    username = forms.CharField(label="用户名", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
class EmailForm(forms.Form):
    """用于输入邮箱的表单"""
    email = forms.EmailField(label="email", required=True)

class SecurityQuestionForm(forms.Form):
    """用于输入安全问题答案和新密码的表单"""
    security_answer = forms.CharField(max_length=255, required=True, label="Security Answer",
                                      widget=forms.TextInput(attrs={'class': 'form-control'}))
    new_password = forms.CharField(label="New password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
