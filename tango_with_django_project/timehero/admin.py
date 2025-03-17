from django.contrib import admin
from .models import User, Task, Achievement,AchievementProgress,Competition,CompetitionRanking,Badge
class AchievementProgressInline(admin.TabularInline):
    model = AchievementProgress
    extra = 0 
    can_delete = False
    readonly_fields = ('achievement', 'unlocked', 'unlocked_at')

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'level', 'exp')
    inlines = [AchievementProgressInline] 
    
@admin.register(CompetitionRanking)
class CompetitionRankingAdmin(admin.ModelAdmin):
    list_display = ("user", "experience", "rank") 

admin.site.register(User)
admin.site.register(Task)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Achievement)
admin.site.register(AchievementProgress) 
admin.site.register(Competition)
admin.site.register(Badge)
