# serializers.py
from rest_framework import serializers
from .models import *

class TaskSerializer(serializers.ModelSerializer):
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'difficulty','priority','difficulty_display', 'is_completed', 'start_date','due_date', 'position_x', 'position_y','tags','checklist','notes']
        extra_kwargs = {'user': {'read_only': True}}
    def get_remaining_time(self, obj):
        return obj.remaining_time()
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'level', 'exp', 'hp']

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description']