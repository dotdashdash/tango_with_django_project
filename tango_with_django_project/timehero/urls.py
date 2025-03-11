from django.urls import path
from .views import password_reset_view

urlpatterns = [
    # ... existing url patterns ...
    path('password-reset/', password_reset_view, name='password_reset'),
] 