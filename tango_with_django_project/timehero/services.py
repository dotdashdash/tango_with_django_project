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
    Task=apps.get_model('timehero','Task')
    task.is_completed = True
    task.save()

    user = task.user
    user.exp += task.difficulty * 10  # 经验值计算
    unlocked_feature = check_level_up(user)  # 检查是否升级
    return unlocked_feature  # 返回解锁的新功能（如果有）

def check_level_up(user):
    """
    玩家升级逻辑：
    - 每升一级需要 level * 100 经验值
    - 每次升级回复 1 点 HP（最多 5）
    - 根据等级解锁新功能
    """
    if user.exp >= user.level * 100:
        user.exp -= user.level * 100
        user.level += 1
        user.hp = min(user.hp + 1, 5)  # HP 上限 5
        
        unlocked_feature = LEVEL_REWARDS.get(user.level, None)
        user.save()
        return unlocked_feature  # 如果解锁了新功能，返回它
    return None
def process_tasks_for_dashboard(tasks):
    """
    处理任务数据，确保 tags、checklist 以列表形式返回，避免 Django 模板 split 过滤器问题
    """
    for task in tasks:
        # 去掉多余空格，确保 tags、checklist 是干净的列表
        task.tags_list = [tag.strip() for tag in task.tags.split(",")] if task.tags else []
        task.checklist_items = [item.strip() for item in task.checklist.split("\n")] if task.checklist else []
        task.notes_content = task.notes.strip() if task.notes else ""

    return tasks

