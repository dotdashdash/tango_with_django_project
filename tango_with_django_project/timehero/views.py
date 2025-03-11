# views.py
import json

from django.http import JsonResponse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from .services import evaluate_difficulty,complete_task,process_tasks_for_dashboard,check_level_up,get_user_achievements
from .signals import *
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .models import User
from .forms import UserRegisterForm, UserLoginForm,  EmailForm, SecurityQuestionForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.http import JsonResponse    
def index(request):
    return render(request, 'index.html')
def register_view(request):
    """用户注册"""
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 自动登录
            messages.success(request, "注册成功，欢迎加入！")
            return redirect("dashboard")
    else:
        form = UserRegisterForm()
    return render(request, "signup.html", {"form": form})

class PixelLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = UserLoginForm
    success_url = reverse_lazy('dashboard')
    
@login_required  # 确保用户必须登录才能访问
def dashboard_view(request):
    tasks = Task.objects.filter(user=request.user)  # 获取当前用户的任务
    tasks = process_tasks_for_dashboard(tasks)
    return render(request, "dashboard.html")

class PixelLogoutView(LogoutView):
    next_page = reverse_lazy('index')

class TaskViewSet(viewsets.ModelViewSet):
    """ 任务视图集 """
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        """ 在创建任务时自动计算难度 """
        user = self.request.user if self.request.user.is_authenticated else None
        if user is None:
            return Response({"error": "User must be authenticated"}, status=400)  # 防止匿名用户创建任务
        
        priority = self.request.data.get("priority", "false").lower() == "true"
        start_date = self.request.data.get("start_date", timezone.now())  # 默认当前时间
        due_date = self.request.data.get("due_date", None)

        tags = self.request.data.get("tags", "").strip()  # 获取 tags
        checklist = self.request.data.get("checklist", "").strip()  # 获取 checklist
        notes = self.request.data.get("notes", "").strip()  # 获取 notes


        task = serializer.save(user=user, start_date=start_date, due_date=due_date, priority=priority,tags=tags,checklist=checklist,notes=notes)
        task.difficulty = evaluate_difficulty(task.title, start_date, due_date, priority)
        task.save()

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """ 完成任务后计算经验值，并检查是否升级 """
        task = self.get_object()

        if task.is_completed:
            return Response({"status": "already completed"}, status=400)

        # ✅ 调用 `services.py` 里的 `complete_task`
        result = complete_task(task)

        # ✅ 确保 `Response` 直接返回 `result`
        return Response(result)  


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

def check_username(request):
    username = request.GET.get('value', None)
    if username and User.objects.filter(username=username).exists():
        return JsonResponse({'available': False})
    return JsonResponse({'available': True})

def check_email_exists(email):
    try:
        user = User.objects.get(email=email)
        return user
    except User.DoesNotExist:
        return None

def password_reset_email_view(request):
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = check_email_exists(email)
            if user:
                request.session['reset_user_id'] = user.id
                return redirect('password_reset_security_question')
            else:
                messages.error(request, "The email is not registered.")
        else:
            messages.error(request, "Please enter a valid email address.")
    else:
        form = EmailForm()
    return render(request, "passwordreset_email.html", {"form": form})


def password_reset_security_question_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'message': 'Session expired. Please start over.'})
        return redirect('password_reset_email')

    user = get_object_or_404(User, id=user_id)

    # Check if account is locked
    if user.is_locked:
        message = "Your account is locked due to too many failed attempts. Please try again later."
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'message': message})
        messages.error(request, message)
        return redirect('login')

    if request.method == "POST":
        if request.headers.get('Content-Type') == 'application/json':
            # Process API request
            data = json.loads(request.body)
            security_answer = data.get('security_answer')
            new_password = data.get('new_password')

            # Check answer attempt count
            if user.security_answer_attempts >= 3:
                user.is_locked = True
                user.save()
                return JsonResponse({
                    'success': False,
                    'message': "Your account is locked due to too many failed attempts. Please try again later.",
                    'redirect_url': '/login/'
                })

            if user.security_answer == security_answer:
                user.set_password(new_password)
                user.security_answer_attempts = 0  # Reset counter
                user.save()
                return JsonResponse({
                    'success': True,
                    'message': "Password reset successfully!",
                    'redirect_url': '/login/'
                })
            else:
                user.security_answer_attempts += 1
                user.last_attempt_time = timezone.now()
                user.save()
                return JsonResponse({
                    'success': False,
                    'message': "Incorrect answer. Please try again."
                })
        else:
            # Process traditional form submission (fallback)
            form = SecurityQuestionForm(request.POST)
    else:
        form = SecurityQuestionForm()

    return render(request, "passwordreset_security_question.html", {
        "form": form,
        "security_question": user.security_question
    })
def ajax_check_email(request):
    email = request.GET.get('email', None)
    if email and User.objects.filter(email=email).exists():
        return JsonResponse({'available': False})
    return JsonResponse({'available': True})

    
def user_achievements_view(request):
    """ 返回 JSON 而不是模板 """
    user = request.user
    if not user.is_authenticated:
        # 若要阻止匿名用户，直接返回空或 401
        return JsonResponse({"achievements": []}, status=200)

    achievements = get_user_achievements(user)
    return JsonResponse({"achievements": achievements}, status=200)