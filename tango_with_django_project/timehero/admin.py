from django.contrib import admin
from .models import User, Task, Achievement,AchievementProgress  # 确保导入了所有模型
class AchievementProgressInline(admin.TabularInline):
    model = AchievementProgress
    extra = 0  # 不显示额外空白行
    can_delete = False
    readonly_fields = ('achievement', 'unlocked', 'unlocked_at')

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'level', 'exp')
    inlines = [AchievementProgressInline]  # 让 `User` 详情页里显示 `AchievementProgress`
admin.site.register(User)
admin.site.register(Task)
# admin.site.register(Achievement)

admin.site.unregister(User)  # 取消默认的 User 注册
admin.site.register(User, CustomUserAdmin)
admin.site.register(Achievement)  # 仍然保持 `Achievement` 可管理
admin.site.register(AchievementProgress)  # 让 `AchievementProgress` 也可以独立管理

