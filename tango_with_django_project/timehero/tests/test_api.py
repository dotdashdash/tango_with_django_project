from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from timehero.models import User, Task
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from timehero.models import User, Task
from django.urls import reverse
from rest_framework.test import APIClient
from django.test import TestCase
import json

class UserAPITest(APITestCase):
    def setUp(self):
        """创建测试用户"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass@")
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        """测试获取个人信息"""
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["username"], self.user.username)

class TaskAPITest(APITestCase):
    def setUp(self):
        """创建测试用户和任务"""
        self.user = User.objects.create_user(username="taskuser", email="task@example.com", password="testpass@")
        self.client.force_authenticate(user=self.user)
        self.task_data = {
            "title": "Study for exam",
            "description": "Prepare for the data science exam",
            "start_date": "2025-03-13T12:00:00Z",
            "due_date": "2025-03-14T12:00:00Z",
            "priority": "true",
        }

    def test_create_task(self):
        """测试创建任务"""
        response = self.client.post("/api/tasks/", self.task_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        task = Task.objects.first()
        self.assertEqual(task.title, "Study for exam")
        # self.assertEqual(task.priority, True)
        
        
User = get_user_model()

class UserAPITest(TestCase):
    """ 测试用户 API 相关功能 """

    def setUp(self):
        """ 创建测试用户 """
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            security_question="What is the name of your first pet?",  # ✅ 统一密保问题
            security_answer="fluffy",  # ✅ 统一小写
        )
        self.client.login(username="testuser", password="testpass123")

    def test_get_profile(self):
        """ 测试获取个人信息 """
        url = reverse("user_achievements")  # ✅ 这里使用正确的 API URL
        response = self.client.get(url)

        print("Response JSON:", response.json())  # ✅ 调试 API 返回值

        self.assertEqual(response.status_code, 200)
        self.assertIn("achievements", response.json())  # ✅ 确保返回 `achievements` 字段

    def test_password_reset_security_question_correct(self):
        """ 测试密保问题正确答案 """
        
        # ✅ 确保 session 里有 `reset_user_id`
        session = self.client.session
        session["reset_user_id"] = self.user.id  
        session.save()

        url = reverse("password_reset_security_question")  # ✅ 确保 URL 反解析正确

        response = self.client.post(
            url,
            json.dumps({"security_answer": "fluffy", "new_password": "NewPass123!"}),  # ✅ 统一小写
            content_type="application/json",
        )

        print("Response JSON:", response.json())  # ✅ 打印 API 返回值，排查错误

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])  # ✅ 预期返回 `success: True`

    def test_password_reset_security_question_wrong(self):
        """ 测试密保问题错误答案 """

        # ✅ 确保 session 里有 `reset_user_id`
        session = self.client.session
        session["reset_user_id"] = self.user.id
        session.save()

        url = reverse("password_reset_security_question")

        response = self.client.post(
            url,
            json.dumps({"security_answer": "wrong_answer", "new_password": "NewPass123!"}),
            content_type="application/json",
        )

        print("Response JSON:", response.json())

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["success"])  # ✅ 预期返回 `success: False`

    def test_check_email_exists(self):
        """ 测试 check_email_exists 方法 """
        from timehero.views import check_email_exists
        user = check_email_exists("test@example.com")
        self.assertIsNotNone(user)  # ✅ 确保用户存在

        non_user = check_email_exists("notexists@example.com")
        self.assertIsNone(non_user)  # ✅ 确保未注册的用户返回 None


class TaskAPITest(TestCase):
    """ 测试任务 API 相关功能 """

    def setUp(self):
        """ 创建测试用户 """
        self.user = User.objects.create_user(username="taskuser", email="task@example.com", password="testpass@")
        self.client.login(username="taskuser", password="testpass@")

    def test_create_task(self):
        """ 测试创建任务 """
        url = reverse("task-list")  # ✅ 任务创建 API 路由
        data = {
            "title": "Test Task",
            "description": "This is a test task",
            "difficulty": 2,
            "is_completed": False
        }

        response = self.client.post(url, json.dumps(data), content_type="application/json")

        print("Response JSON:", response.json())  # ✅ 调试 API 返回值

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "Test Task")