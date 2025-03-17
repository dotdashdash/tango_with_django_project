# models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
import random
# from .services import evaluate_difficulty
from django.conf import settings


class User(AbstractUser):
    level = models.IntegerField(default=1)
    exp = models.IntegerField(default=0)
    hp = models.IntegerField(default=5)
    achievements = models.ManyToManyField('Achievement', through='AchievementProgress')
    groups = models.ManyToManyField(Group, 
                                    verbose_name='groups',
                                    blank=True,
                                    help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                                    related_name="timehero_user_groups",
                                    related_query_name="user",)
    user_permissions = models.ManyToManyField(Permission,
                                    verbose_name='user permissions',
                                    blank=True,
                                    help_text='Specific permissions for this user.',
                                    related_name="timehero_user_permissions",
                                    related_query_name="user",)
    security_question = models.CharField(max_length=255, blank=True)
    security_answer = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    security_answer_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    last_attempt_time = models.DateTimeField(null=True, blank=True)

    def reset_password(self, email, new_password, security_answer):
        try:
            user = User.objects.get(email=email)
            if user.security_answer == security_answer:
                user.set_password(new_password)
                user.save()
                return True
        except User.DoesNotExist:
            pass
        return False

    def get_security_question(self):
        return self.security_question

    

# class Task(models.Model):
#     DIFFICULTY_CHOICES = [
#         (1, '⭐'), 
#         (2, '⭐⭐'),
#         (3, '⭐⭐⭐')
#     ]
    
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=32)
#     description = models.TextField(blank=True)
#     difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
#     is_completed = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     due_date = models.DateTimeField(null=True, blank=True)
class Task(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    difficulty = models.IntegerField(default=1)  
    # duration = models.IntegerField(default=30)  
    priority = models.BooleanField(default=False)  
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_count = models.IntegerField(default=0)  # dump
    failed_count = models.IntegerField(default=0)  # dump
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    position_x = models.IntegerField(null=True, blank=True)
    position_y = models.IntegerField(null=True, blank=True)
    tags = models.CharField(max_length=255, blank=True, null=True)  
    checklist = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True) 


    def complete_task(self):
        """ completed...then check if level up """
        from .services import complete_task  # !circular import
        return complete_task(self)

    def save(self, *args, **kwargs):
        from .services import evaluate_difficulty
        self.priority = self.priority if self.priority is not None else False
        self.difficulty = evaluate_difficulty(self.title, self.start_date,self.due_date, self.priority)
        super().save(*args, **kwargs)



    def __str__(self):
        return self.title

class Achievement(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    unlock_condition = models.IntegerField(default=0)  
    unlocked_at=models.DateTimeField(auto_now_add=True, null=True, blank=True)

class AchievementProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked = models.BooleanField(default=False)
    unlocked_at = models.DateTimeField(null=True, blank=True)
    
class Competition(models.Model):
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField(default=now() + timedelta(days=7))  # weekly
    is_active = models.BooleanField(default=True)  # always active

    def __str__(self):
        return f"Weekly Competition ({self.start_date.date()} - {self.end_date.date()})"

class CompetitionRanking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    experience = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user',)  # user unique

    def __str__(self):
        return f"{self.user.username} - {self.experience} XP (Rank {self.rank})"

class Badge(models.Model):
    """ 竞赛奖励徽章 """
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=255)  
    ranking_threshold = models.IntegerField()  

    def __str__(self):
        return self.name