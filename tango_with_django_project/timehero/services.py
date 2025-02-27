from datetime import datetime
from django.apps import apps

# 经验值奖励规则
LEVEL_REWARDS = {
    2: "🌞 Daily Tasks Unlocked! Set tasks to repeat daily.",
    5: "📋 Batch Task Creation Unlocked! Create multiple tasks at once.",
    10: "⏰ Task Reminders Unlocked! Get automatic notifications.",
    15: "🔥 Task Prioritization Unlocked! Mark high-priority tasks.",
    20: "🏆 Achievement Display Unlocked! View your unlocked achievements.",
    25: "🎁 Hidden Bonus Tasks Unlocked! Find special challenges.",
    30: "🗺️ Adventure Mode Unlocked! Explore and find tasks in the world.",
    40: "⚔️ Boss Mode Unlocked! Special high-reward tasks appear.",
}

MAX_HEALTH = 5
MAX_LEVEL = 100
MAX_STAT_POINTS = MAX_LEVEL
MAX_LEVEL_HARD_CAP = 9999

def to_next_level(level):
    """计算下一级所需的经验值"""
    if level < 5:
        return 25 * level
    elif level == 5:
        return 150
    else:
        return round(((level ** 2) * 0.25 + 10 * level + 139.75) / 10) * 10

def cap_by_level(level):
    """限制等级不超过最大等级"""
    return min(level, MAX_LEVEL)

# def auto_allocate(user):
#     """自动分配属性点的逻辑"""
#     points_to_allocate = user.stat_points
#     user.strength += points_to_allocate // 4
#     user.intelligence += points_to_allocate // 4
#     user.constitution += points_to_allocate // 4
#     user.perception += points_to_allocate // 4
#     user.stat_points = 0

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


def complete_task(task):
    """
    任务完成后：
    - 标记任务完成
    - 更新用户经验值
    - 检查用户是否升级
    """
    Task = apps.get_model('timehero', 'Task')
    task.is_completed = True
    task.save()

    user = task.user
    user.exp += task.difficulty * 1000  # 经验值计算
    unlocked_features = []

    # 升级逻辑
    experience_to_next_level = to_next_level(user.level)
    while user.exp >= experience_to_next_level:
        user.exp -= experience_to_next_level
        user.level = min(user.level + 1, MAX_LEVEL_HARD_CAP)
        user.hp = min(user.hp + 1, MAX_HEALTH)  # 升级时恢复生命值

        # 检查是否解锁新功能
        unlocked_feature = LEVEL_REWARDS.get(user.level)
        if unlocked_feature:
            unlocked_features.append(unlocked_feature)

        experience_to_next_level = to_next_level(user.level)

    user.save()
    return unlocked_features  # 返回解锁的新功能列表