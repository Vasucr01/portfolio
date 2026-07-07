from django.contrib import admin
import cloudinary.uploader
from .models import Profile, Skill, Project, Visitor


def upload_to_cloudinary(file_obj, folder):
    """Upload a file-like object to Cloudinary and return its secure URL."""
    result = cloudinary.uploader.upload(
        file_obj,
        folder=folder,
        resource_type='auto',
    )
    return result.get('secure_url', '')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'hero_title')
    search_fields = ('name', 'about_text')

    def save_model(self, request, obj, form, change):
        # Handle about_image upload directly via Cloudinary SDK
        if 'about_image' in request.FILES:
            url = upload_to_cloudinary(request.FILES['about_image'], 'profile')
            # Store the URL string directly; avoid Django FileSystemStorage
            obj.about_image = url

        # Handle cv_file upload directly via Cloudinary SDK
        if 'cv_file' in request.FILES:
            url = upload_to_cloudinary(request.FILES['cv_file'], 'cv')
            obj.cv_file = url

        super().save_model(request, obj, form, change)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage', 'order')
    search_fields = ('name',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    search_fields = ('title', 'description')

    def save_model(self, request, obj, form, change):
        # Handle project image upload directly via Cloudinary SDK
        if 'image' in request.FILES:
            url = upload_to_cloudinary(request.FILES['image'], 'projects')
            obj.image = url

        super().save_model(request, obj, form, change)


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'visited_at', 'path')
    readonly_fields = ('ip_address', 'user_agent', 'visited_at', 'path')

    def has_add_permission(self, request):
        return False
