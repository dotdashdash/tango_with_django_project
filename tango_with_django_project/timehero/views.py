# views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from .services import evaluate_difficulty, complete_task, to_next_level, cap_by_level, MAX_STAT_POINTS, MAX_HEALTH
from .signals import *
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .models import User
from .forms import UserRegisterForm, UserLoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

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

        task = serializer.save(user=user, start_date=start_date, due_date=due_date, priority=priority)
        task.difficulty = evaluate_difficulty(task.title, start_date, due_date, priority)
        task.save()


    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """ 完成任务后计算经验值，并检查是否升级 """
        task = self.get_object()
        if not task.is_completed:
            task.is_completed = True
            task.save()

            user = task.user
            user.exp += task.difficulty * 1000

            # 升级逻辑
            experience_to_next_level = to_next_level(user.level)
            leveled_up = False

            while user.exp >= experience_to_next_level:
                user.exp -= experience_to_next_level
                user.level = cap_by_level(user.level + 1)
                leveled_up = True

                experience_to_next_level = to_next_level(user.level)
                user.hp = MAX_HEALTH
                #
                # allocated_stat_points = user.strength + user.intelligence + user.constitution + user.perception
                # total_stat_points = allocated_stat_points + user.stat_points
                #
                # if total_stat_points < MAX_STAT_POINTS:
                #     if user.automatic_allocation:
                #         auto_allocate(user)
                #     else:
                #         user.stat_points = user.level - allocated_stat_points
                #         total_stat_points = user.stat_points + allocated_stat_points
                #
                #         if total_stat_points > MAX_STAT_POINTS:
                #             user.stat_points = MAX_STAT_POINTS - allocated_stat_points
                #
                #         if user.stat_points < 0:
                #             user.stat_points = 0
            user.save()

            if leveled_up:
                # 记录升级事件或发送通知
                pass

        return Response({"status": "completed"})

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)