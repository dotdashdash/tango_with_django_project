# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # 初始成就进度
        for achievement in Achievement.objects.filter(unlock_condition__lte=instance.level):
            AchievementProgress.objects.create(
                user=instance, 
                achievement=achievement
            )

def check_level_up(user):
    exp_needed = user.level * 100
    if user.exp >= exp_needed:
        user.level += 1
        user.exp -= exp_needed
        user.hp = min(user.hp + 1, 5)  # 最大HP为5
        user.save()

def check_achievements(user):
    for progress in user.achievementprogress_set.filter(unlocked=False):
        condition = progress.achievement.unlock_condition
        if eval(condition, None, {'user': user}):
            progress.unlocked = True
            progress.save()