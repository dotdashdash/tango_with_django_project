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
# from django.contrib import admin
# from django.urls import path
# from django.urls import include
# from game.views import index,get_song_view, check_answer
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('',index, name='index'),
#     # path('game/', include('game.urls')),
#     path("get_song/", get_song_view, name="get_song"),
#     path("check_answer/", check_answer, name="check_answer"),


# ]
# urls.py
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
    # path("achievements/", achievement_list, name="achievement-list"),
    # path('api/profile/', UserViewSet.as_view({'get': 'profile'})),
    # path('create/', TaskViewSet.as_view({'post':'create'}), name="create_task"),
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)