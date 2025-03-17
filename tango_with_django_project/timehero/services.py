from datetime import datetime

from django.apps import apps
import math
from django.utils.timezone import now


def evaluate_difficulty(title, start_date, due_date, priority):
    """
    calculate the difficulty of a task based on its title, start date, due date, and priority
    """
    keywords_hard = ["report", "study", "presentation", "deadline", "research"]
    keywords_medium = ["exercise", "meeting", "cleaning", "shopping"]

    difficulty = 1  # default easy
    if not start_date or not due_date:
        return difficulty

    # calculate duration in minutes
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(due_date, str):
        due_date = datetime.fromisoformat(due_date)

    duration = int((due_date - start_date).total_seconds() // 60)

    # match keywords to evaluate difficulty
    if any(word in title.lower() for word in keywords_hard):
        difficulty = 3
    elif any(word in title.lower() for word in keywords_medium):
        difficulty = 2

    # time-based evaluation
    if duration > 120:
        difficulty = max(difficulty, 3)
    elif duration > 60:
        difficulty = max(difficulty, 2)

    # high priority tasks are harder
    if priority:
        difficulty = min(3, difficulty + 1)

    return difficulty


def complete_task(task):
    """
    after a task is completed, update user's experience and check if the user has leveled up
    """
    # Task = apps.get_model('timehero', 'Task')
    task.is_completed = True
    task.save()

    user = task.user
    user.exp += task.difficulty * 10  # ✅ accumulate experience
    user.save()

    new_level, newly_unlocked, all_achievements = check_level_up(user)
    Achievement = apps.get_model("timehero", "Achievement")
    all_achievements = list(
        Achievement.objects.filter(
            achievementprogress__user=user, achievementprogress__unlocked=True
        ).values_list("name", flat=True)
    )

    return {
        "status": "completed",
        "new_level": new_level if new_level else user.level,
        "exp": user.exp,
        "unlocked_features": newly_unlocked,
        "all_achievements": all_achievements,
    }


def check_level_up(user):
    Achievement = apps.get_model(
        "timehero", "Achievement"
    )  # apps.get_model('app_name', 'model_name')
    AchievementProgress = apps.get_model("timehero", "AchievementProgress")

    # define level-up rewards
    LEVEL_REWARDS = {
        2: "🌱 You've reached Level 2! Good start!",
        3: "🌿 Level 3 unlocked! Keep going!",
        4: "🍀 Level 4: Another step forward!",
        5: "🌟 Level 5: Batch Task Creation Unlocked!",
        6: "💪 Level 6: More tasks, more power!",
        7: "🔥 Level 7: Fire up your productivity!",
        8: "🌈 Level 8: Rainbow of possibilities!",
        9: "💡 Level 9: Enlighten your workflow!",
        10: "⏰ Level 10: Task Reminders Unlocked!",
        11: "⚡ Level 11: Lightning-speed progress!",
        12: "🔮 Level 12: Foresee bigger tasks!",
        13: "🐲 Level 13: Facing bigger challenges!",
        14: "🎯 Level 14: Ultra focus unlocked!",
        15: "🏆 Level 15: Achievement Display Unlocked!",
        16: "🎁 Level 16: Hidden Bonus Tasks Unlocked!",
        17: "🌍 Level 17: Adventure Mode Unlocked!",
        18: "🎉 Level 18: Surprise Party for your tasks!",
        19: "🚀 Level 19: Rocket your efficiency!",
        20: "⚔ Level 20: Boss Mode Unlocked! Special high-reward tasks appear.",
    }

    old_level = user.level
    new_level = new_level = math.floor(user.exp / 100) + 1
    newly_unlocked = []  # save newly unlocked achievements

    # check if user has leveled up
    for lvl, reward in LEVEL_REWARDS.items():
        if old_level < lvl <= new_level:  # level changed
            achievement, created = Achievement.objects.get_or_create(
                name=reward, unlock_condition=int(lvl)
            )
            progress, created = AchievementProgress.objects.get_or_create(
                user=user, achievement=achievement
            )

            if created or not progress.unlocked:
                progress.unlocked = True
                progress.unlocked_at = now()
                progress.save()
                newly_unlocked.append(
                    {
                        "name": achievement.name,
                        "unlocked_at": progress.unlocked_at.strftime("%Y-%m-%d %H:%M"),
                    }
                )  # only save newly unlocked achievements
    all_achievements = list(
        Achievement.objects.filter(
            achievementprogress__user=user, achievementprogress__unlocked=True
        ).values_list("name", flat=True)
    )
    if new_level > old_level:
        user.level = new_level
        user.save()

    # return old_level, []
    return new_level, newly_unlocked, all_achievements


def process_tasks_for_dashboard(tasks):
    """
    deal with task data to be displayed on the dashboard
    """
    for task in tasks:
        task.tags_list = (
            [tag.strip() for tag in task.tags.split(",")] if task.tags else []
        )
        task.checklist_items = (
            [item.strip() for item in task.checklist.split("\n")]
            if task.checklist
            else []
        )
        task.notes_content = task.notes.strip() if task.notes else ""

    return tasks


def get_user_achievements(user):
    """get current user's unlocked achievements"""
    AchievementProgress = apps.get_model("timehero", "AchievementProgress")
    achievements = AchievementProgress.objects.filter(
        user=user,
        unlocked=True,
        # ).values_list("achievement__name", flat=True)
    ).select_related("achievement")
    return [
        {
            "name": ap.achievement.name,
            # "description": ap.achievement.description,
            "unlocked_at": (
                ap.unlocked_at.strftime("%Y-%m-%d %H:%M")
                if ap.unlocked_at
                else "unknown time"
            ), 
        }
        for ap in achievements
    ]


def update_competition_ranking(user, exp_gained):
    """after a task is completed, update user's experience and check if the user has leveled up"""
    ranking, created = CompetitionRanking.objects.get_or_create(user=user)

    ranking.experience += exp_gained
    ranking.save()

    # renew ranking
    all_rankings = CompetitionRanking.objects.all().order_by("-experience")
    for index, rank in enumerate(all_rankings, start=1):
        rank.rank = index
        rank.save()


from .models import CompetitionRanking


def reset_weekly_ranking():
    """clear all experience and ranking for weekly competition"""
    CompetitionRanking.objects.all().update(experience=0, rank=0)
