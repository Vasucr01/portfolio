from django.contrib import admin
from .models import Profile, Skill, Project, Visitor

admin.site.register(Profile)
admin.site.register(Skill)
admin.site.register(Project)

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'visited_at', 'path')
    readonly_fields = ('ip_address', 'user_agent', 'visited_at', 'path')
    
    def has_add_permission(self, request):
        return False
