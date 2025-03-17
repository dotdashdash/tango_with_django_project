# views.py
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
from .forms import UserRegisterForm, UserLoginForm,SecurityQuestionForm,EmailForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
import json
from django.contrib.auth import get_user_model

def index(request):
    return render(request, 'index.html')
def register_view(request):
    """register"""
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # login after register
            messages.success(request, "Welcome！")
            return redirect("dashboard")
    else:
        form = UserRegisterForm()
    return render(request, "signup.html", {"form": form})

class PixelLoginView(LoginView):
    # template_name = 'login.html'
    authentication_form = UserLoginForm
    success_url = reverse_lazy('dashboard')
    
@login_required  # must login
def dashboard_view(request):
    tasks = Task.objects.filter(user=request.user)  # get all tasks
    tasks = process_tasks_for_dashboard(tasks) 
    return render(request, "dashboard.html")

class PixelLogoutView(LogoutView):
    next_page = reverse_lazy('index')

class TaskViewSet(viewsets.ModelViewSet):
    """ tast api """
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        """ use evaluate_difficulty to calculate difficulty """
        user = self.request.user if self.request.user.is_authenticated else None
        if user is None:
            return Response({"error": "User must be authenticated"}, status=400)
        
        priority = self.request.data.get("priority", "false").lower() == "true"
        start_date = self.request.data.get("start_date", timezone.now())  # default to now
        due_date = self.request.data.get("due_date", None)
        
        tags = self.request.data.get("tags", "").strip() 
        checklist = self.request.data.get("checklist", "").strip() 
        notes = self.request.data.get("notes", "").strip()


        task = serializer.save(user=user, start_date=start_date, due_date=due_date, priority=priority,tags=tags,checklist=checklist,notes=notes)
        task.difficulty = evaluate_difficulty(task.title, start_date, due_date, priority)
        task.save()

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """ calculate experience and check level up """
        task = self.get_object()

        if task.is_completed:
            return Response({"status": "already completed"}, status=400)

        # ✅ `services.py` `complete_task`
        result = complete_task(task)

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
    
def user_achievements_view(request):
    """ return json """
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"achievements": []}, status=200)

    achievements = get_user_achievements(user)
    return JsonResponse({"achievements": achievements}, status=200)
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
        return redirect('index')

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
                    'redirect_url': '/index/'
                })

            if user.security_answer == security_answer:
                user.set_password(new_password)
                user.security_answer_attempts = 0  # Reset counter
                user.save()
                return JsonResponse({
                    'success': True,
                    'message': "Password reset successfully!",
                    'redirect_url': '/index/'
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
        return JsonResponse({'exists': True})
    return JsonResponse({'exists': False})

def get_ranking(request):
    """
    return top 10 ranking
    [
      {"username": "aaa", "experience": 120, "rank": 1, "is_current_user": false},
      ...
      {"username": "...", "experience": 0, "rank": -1, "is_ellipsis": true},
      {"username": "testuser", "experience": 20, "rank": 13, "is_current_user": true}
    ]
    """
    current_user = request.user if request.user.is_authenticated else None

    # 1) get all users
    User = get_user_model()
    all_users = User.objects.all()

    # 2)merge user and experience
    user_experiences = []
    for user in all_users:
        try:
            cr = CompetitionRanking.objects.get(user=user)
            exp = cr.experience
        except CompetitionRanking.DoesNotExist:
            exp = 0  # no data=> 0
        user_experiences.append((user, exp))

    # 3) descending sort
    user_experiences.sort(key=lambda x: x[1], reverse=True)

    # 4) calculate rank
    data = []
    rank = 1
    for (user, exp) in user_experiences:
        data.append({
            "username": user.username,
            "experience": exp,
            "rank": rank,
            # highlight current user
            "is_current_user": (current_user == user),
            "is_ellipsis": False,
        })
        rank += 1

    top_10 = data[:10]

    # check if current user is in top 10
    if current_user:
        user_in_top_10 = any(d["is_current_user"] for d in top_10)
        if not user_in_top_10:
            # 1. find current user entry
            try:
                current_user_entry = next(d for d in data if d["is_current_user"])
            except StopIteration:
                current_user_entry = None

            # 2. insert after 10th
            if current_user_entry:
                top_10.append({
                    "username": "...",
                    "experience": 0,
                    "rank": -1,
                    "is_current_user": False,
                    "is_ellipsis": True,
                })
                top_10.append(current_user_entry)

    return JsonResponse(top_10, safe=False)


from django.utils.timezone import now

def get_competition_timer(request):
    """ return end date of the week """
    end_time = now() + timedelta(days=7 - now().weekday())  # calculate end of the week
    return JsonResponse({"end_date": end_time.isoformat()})