from django.test import TestCase
from django.contrib.auth import get_user_model
from timehero.forms import UserRegisterForm, UserLoginForm, EmailForm, SecurityQuestionForm

User=get_user_model()
class UserRegisterFormTest(TestCase):
    def test_valid_registration_form(self):
        """测试有效的注册表单"""
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "TestPassword123",
            "password2": "TestPassword123",
            "security_question": "What is the name of your first pet？",
            "security_answer": "Charlie"
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_registration_password_mismatch(self):
        """测试无效注册 - 密码不匹配"""
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "TestPassword123",
            "password2": "WrongPassword",
            "security_question": "What is the name of your first pet？",
            "security_answer": "Charlie"
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_invalid_registration_missing_field(self):
        """测试无效注册 - 缺少字段"""
        form_data = {
            "username": "testuser",
            "email": "",
            "password1": "TestPassword123",
            "password2": "TestPassword123",
            "security_question": "What is the name of your first pet？",
            "security_answer": "Charlie"
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

class UserLoginFormTest(TestCase):
    def setUp(self):
        """创建一个测试用户"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="TestPassword123")

    def test_valid_login_form(self):
        """测试有效的登录表单"""
        form_data = {"username": "testuser", "password": "TestPassword123"}
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_login_form_empty_fields(self):
        """测试无效的登录表单 - 空字段"""
        form_data = {"username": "", "password": ""}
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())

class EmailFormTest(TestCase):
    def test_valid_email_form(self):
        """测试有效邮箱输入"""
        form_data = {"email": "test@example.com"}
        form = EmailForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email_form(self):
        """测试无效邮箱输入（格式错误）"""
        form_data = {"email": "invalid-email"}
        form = EmailForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

class SecurityQuestionFormTest(TestCase):
    def test_valid_security_question_form(self):
        """测试密保问题答案输入"""
        form_data = {
            "security_answer": "Charlie",
            "new_password": "NewSecurePass123"
        }
        form = SecurityQuestionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_security_question_form_missing_fields(self):
        """测试密保问题答案为空"""
        form_data = {"security_answer": "", "new_password": ""}
        form = SecurityQuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("security_answer", form.errors)
        self.assertIn("new_password", form.errors)
