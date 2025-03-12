from django.test import TestCase
from django.utils.timezone import now
from timehero.models import User, Task, Achievement, AchievementProgress

class UserModelTest(TestCase):
    def setUp(self):
        """ 创建测试用户 """
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass@")
        self.user.security_question = "What is the name of your first pet？"
        self.user.security_answer = "Fluffy"
        self.user.save()

    def test_reset_password_success(self):
        """ 测试用户密码重置功能 """
        reset = self.user.reset_password(email="test@example.com", new_password="newpass1@", security_answer="Fluffy")
        self.assertTrue(reset)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass1@"))

    def test_reset_password_wrong_answer(self):
        """ 测试密码重置时答案错误 """
        reset = self.user.reset_password(email="test@example.com", new_password="newpass", security_answer="WrongAnswer")
        self.assertFalse(reset)

    def test_get_security_question(self):
        """ 测试获取安全问题 """
        self.assertEqual(self.user.get_security_question(), "What is the name of your first pet？")


# class TaskModelTest(TestCase):
#     def setUp(self):
#         """ 创建测试用户和任务 """
#         self.user = User.objects.create_user(username="taskuser", email="task@example.com", password="testpass")
#         self.task = Task.objects.create(
#             user=self.user,
#             title="Test Task",
#             description="This is a test task",
#             difficulty=2,
#             is_completed=False
#         )

#     def test_task_creation(self):
#         """ 测试任务创建 """
#         self.assertEqual(self.task.title, "Test Task")
#         self.assertEqual(self.task.difficulty, 2)
#         self.assertFalse(self.task.is_completed)

#     def test_complete_task(self):
#         """ 测试任务完成功能 """
#         self.task.is_completed = True
#         self.task.save()
#         self.assertTrue(self.task.is_completed)


# class AchievementModelTest(TestCase):
#     def setUp(self):
#         """ 创建测试用户和成就 """
#         self.user = User.objects.create_user(username="achiever", email="achieve@example.com", password="testpass")
#         self.achievement = Achievement.objects.create(name="First Task", description="Complete your first task")

#     def test_achievement_progress(self):
#         """ 测试用户成就进度 """
#         progress = AchievementProgress.objects.create(user=self.user, achievement=self.achievement, unlocked=True, unlocked_at=now())
#         self.assertTrue(progress.unlocked)
#         self.assertEqual(progress.achievement.name, "First Task")

