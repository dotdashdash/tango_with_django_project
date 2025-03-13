# """
# URL configuration for tango_with_django_project project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.1/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """

from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from timehero.views import *
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'tasks', TaskViewSet,basename='task')
router.register(r'users', UserViewSet)
# router.register(r'achievements', AchievementViewSet,basename='achievement')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path("signup/", register_view, name="signup"),
    path("login/", PixelLoginView.as_view(), name="login"),
    path("logout/", PixelLogoutView.as_view(), name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path('', index),
    path('api/', include(router.urls)),
    path("api/user/achievements/", user_achievements_view, name="user_achievements"),
    # path('api/check_username/', check_username, name='check_username'),
    path('api/check_email/', check_email_exists, name='check_email'),
    path('password-reset/', password_reset_email_view, name='password_reset_email'),
    path('password-reset/security-question/', password_reset_security_question_view, name='password_reset_security_question'),
    path('api/ajax_check_email/', ajax_check_email, name='ajax_check_email'),
    path('index/', index, name='index'),

    path('api/get_ranking/', get_ranking, name='get_ranking'),
    path('api/get_competition_timer/', get_competition_timer, name='get_competition_timer'),



    # path("achievements/", achievement_list, name="achievement-list"),
    # path('api/profile/', UserViewSet.as_view({'get': 'profile'})),
    # path('create/', TaskViewSet.as_view({'post':'create'}), name="create_task"),
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)