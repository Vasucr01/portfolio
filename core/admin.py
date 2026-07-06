from django.contrib import admin
from .models import Profile, Skill, Project, Visitor

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'hero_title')
    search_fields = ('name', 'about_text')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage', 'order')
    search_fields = ('name',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    search_fields = ('title', 'description')

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'visited_at', 'path')
    readonly_fields = ('ip_address', 'user_agent', 'visited_at', 'path')
    
    def has_add_permission(self, request):
        return False
