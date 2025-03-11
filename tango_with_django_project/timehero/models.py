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
    # duration = models.IntegerField(default=30)  # 预计完成时间（分钟）
    priority = models.BooleanField(default=False)  # 是否高优先级
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_count = models.IntegerField(default=0)  # 任务成功完成的次数
    failed_count = models.IntegerField(default=0)  # 任务失败的次数
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    position_x = models.IntegerField(null=True, blank=True)
    position_y = models.IntegerField(null=True, blank=True)
    tags = models.CharField(max_length=255, blank=True, null=True)  # 用逗号分隔的标签
    checklist = models.TextField(blank=True, null=True)  # 任务清单，每行一个项目
    notes = models.TextField(blank=True, null=True) 


    def complete_task(self):
        """ 任务完成后，更新状态并检查升级 """
        from .services import complete_task  # 避免循环导入
        return complete_task(self)

    def save(self, *args, **kwargs):
        from .services import evaluate_difficulty
        self.priority = self.priority if self.priority is not None else False  # 避免 None
        self.difficulty = evaluate_difficulty(self.title, self.start_date,self.due_date, self.priority)
        super().save(*args, **kwargs)



    def __str__(self):
        return self.title

class Achievement(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    unlock_condition = models.IntegerField()  
    unlocked_at=models.DateTimeField(auto_now_add=True, null=True, blank=True)

class AchievementProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked = models.BooleanField(default=False)
    unlocked_at = models.DateTimeField(null=True, blank=True)