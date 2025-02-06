from django.contrib import admin
from .models import User, Task, Achievement  # 确保导入了所有模型

admin.site.register(User)
admin.site.register(Task)
admin.site.register(Achievement)
