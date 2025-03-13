from datetime import datetime

from django.apps import apps
import math
from django.utils.timezone import now


def evaluate_difficulty(title, start_date, due_date, priority):
    """
    计算任务难度：
    - 关键词匹配（任务名称）
    - 任务持续时间（due_date - start_date）
    - 任务优先级
    """
    keywords_hard = ["report", "study", "presentation", "deadline", "research"]
    keywords_medium = ["exercise", "meeting", "cleaning", "shopping"]

    difficulty = 1  # 默认难度为 Easy

    # 计算任务持续时间（分钟）
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(due_date, str):
        due_date = datetime.fromisoformat(due_date)

    duration = int((due_date - start_date).total_seconds() // 60)

    # 关键词匹配
    if any(word in title.lower() for word in keywords_hard):
        difficulty = 3
    elif any(word in title.lower() for word in keywords_medium):
        difficulty = 2

    # 时间影响难度
    if duration > 120:
        difficulty = max(difficulty, 3)
    elif duration > 60:
        difficulty = max(difficulty, 2)

    # 高优先级任务增加难度
    if priority:
        difficulty = min(3, difficulty + 1)

    return difficulty


# def complete_task(task):
#     """
#     任务完成后：
#     - 标记任务完成
#     - 经验值一直累积
#     - 检查用户是否升级
#     """
#     # Task = apps.get_model('timehero', 'Task')
#     task.is_completed = True
#     task.save()

#     user = task.user
#     user.exp += task.difficulty * 10  # ✅ 经验值不会被扣除
#     user.save()

#     new_level, newly_unlocked, all_achievements = check_level_up(user)
#     Achievement = apps.get_model("timehero", "Achievement")
#     all_achievements = list(
#         Achievement.objects.filter(
#             achievementprogress__user=user, achievementprogress__unlocked=True
#         ).values_list("name", flat=True)
#     )
#     """ 任务完成后，增加经验并更新排行榜 """
#     exp_gained = task.difficulty * 10  # 经验计算规则
#     task.user.exp += exp_gained
#     task.user.save()

#     update_competition_ranking(task.user, exp_gained)

#     return {
#         "status": "completed",
#         "new_level": new_level if new_level else user.level,
#         "exp": user.exp,  # ✅ 确保返回的是累积经验值
#         "unlocked_features": newly_unlocked,
#         "all_achievements": all_achievements,
#     }
def complete_task(task):
    """
    任务完成后：
    - 标记任务完成
    - 给用户增加总经验（User.exp）
    - 给本周排行榜增加周经验（CompetitionRanking.experience）
    - 检查用户是否升级
    """
    task.is_completed = True
    task.save()

    user = task.user
    
    # ① 根据难度定义经验加成
    if task.difficulty == 1:  # Easy
        exp_gained = 20
    elif task.difficulty == 3:  # Hard
        exp_gained = 30
    # else:
    #     exp_gained = 25  # Medium (你可以自行决定)

    # ② 增加用户总经验
    user.exp += exp_gained
    user.save()

    # ③ 更新本周排行榜
    from .services import update_competition_ranking
    update_competition_ranking(user, exp_gained)

    # ④ 检查是否升级
    new_level, newly_unlocked, all_achievements = check_level_up(user)

    # ⑤ 返回给前端的数据
    return {
        "status": "completed",
        "new_level": new_level if new_level else user.level,
        "exp": user.exp,  # 总经验
        "unlocked_features": newly_unlocked,
        "all_achievements": all_achievements,
    }


def check_level_up(user):
    Achievement = apps.get_model(
        "timehero", "Achievement"
    )  # ✅ 通过 `apps.get_model()` 访问模型
    AchievementProgress = apps.get_model("timehero", "AchievementProgress")

    """
    计算玩家的等级（逐级累积需求：1->2 需要 100, 2->3 需要 200, etc.）
    并返回解锁的奖励列表
    """

    # 在方法里内置所有等级对应的奖励，若超出可自行扩充
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

    # 计算“升到 level 级”所需的总经验 = (level-1)*level/2 * 100
    old_level = user.level
    new_level = new_level = math.floor(user.exp / 100) + 1
    newly_unlocked = []  # 存储本次升级解锁的成就

    # 遍历 `LEVEL_REWARDS`，判断是否解锁新成就
    for lvl, reward in LEVEL_REWARDS.items():
        if old_level < lvl <= new_level:  # ✅ 只有从旧等级到新等级之间的才解锁
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
                )  # ✅ 只存储新解锁的成就
    all_achievements = list(
        Achievement.objects.filter(
            achievementprogress__user=user, achievementprogress__unlocked=True
        ).values_list("name", flat=True)
    )
    if new_level > old_level:
        user.level = new_level
        user.save()
    # return new_level, newly_unlocked, all_achievements  # ✅ 必须返回 3 个

    # return old_level, []
    return new_level, newly_unlocked, all_achievements


def process_tasks_for_dashboard(tasks):
    """
    处理任务数据，确保 tags、checklist 以列表形式返回，避免 Django 模板 split 过滤器问题
    """
    for task in tasks:
        # 去掉多余空格，确保 tags、checklist 是干净的列表
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
    """获取当前用户解锁的成就"""
    AchievementProgress = apps.get_model("timehero", "AchievementProgress")
    achievements = AchievementProgress.objects.filter(
        user=user,
        unlocked=True,
        # ).values_list("achievement__name", flat=True)
    ).select_related("achievement")
    # return list(achievements)  # 返回字符串列表
    return [
        {
            "name": ap.achievement.name,
            # "description": ap.achievement.description,
            "unlocked_at": (
                ap.unlocked_at.strftime("%Y-%m-%d %H:%M")
                if ap.unlocked_at
                else "unknown time"
            ),  # 返回格式化时间
        }
        for ap in achievements
    ]

from .models import Competition, CompetitionRanking


def update_competition_ranking(user, exp_gained):
    """ 任务完成后更新排行榜经验 """
    ranking, created = CompetitionRanking.objects.get_or_create(user=user)

    ranking.experience += exp_gained
    ranking.save()

    # 更新所有用户排名
    all_rankings = CompetitionRanking.objects.all().order_by('-experience')
    for index, rank in enumerate(all_rankings, start=1):
        rank.rank = index
        rank.save()
        
        
from django.utils.timezone import now, timedelta
from .models import CompetitionRanking

def reset_weekly_ranking():
    """ 每周清零排行榜经验 """
    CompetitionRanking.objects.all().update(experience=0, rank=0)
