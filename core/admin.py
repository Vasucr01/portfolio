import io
import json
import requests
from django import forms
from django.contrib import admin
from django.contrib import messages
from django.conf import settings
import cloudinary.uploader
from PyPDF2 import PdfReader
import google.generativeai as genai

from .models import Profile, Skill, Project, Visitor, ContactMessage, Experience, Education, Achievement


def upload_to_cloudinary(file_obj, folder):
    """Upload a file-like object to Cloudinary and return its secure URL."""
    try:
        result = cloudinary.uploader.upload(
            file_obj,
            folder=folder,
            resource_type='auto',
        )
        return result.get('secure_url', '')
    except Exception as e:
        print("Cloudinary upload failed:", e)
        return ''


def extract_text_from_pdf(file_stream):
    """Extract text from a PDF file stream using PyPDF2."""
    try:
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception as e:
        print("PDF extraction failed:", e)
        return ""


def run_gemini_population(profile_obj, cv_text, request=None):
    """Query Gemini to parse CV text and populate database records."""
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or getattr(settings, 'GEMINI_API_KEY', '')
    # Check OS environment as fallback
    import os
    if not api_key:
        api_key = os.environ.get('GEMINI_API_KEY', '')

    if not api_key:
        if request:
            messages.warning(
                request,
                "GEMINI_API_KEY is not configured. Saved CV text to chatbot knowledge base, but could not auto-populate other portfolio fields."
            )
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are an expert system that extracts structured information from resume text.
        Analyze this CV text and return a single valid JSON object. Do not include any markdown formatting like ```json or anything else. The output must be pure JSON.
        
        CV TEXT:
        {cv_text}
        
        JSON STRUCTURE:
        {{
            "name": "Full Name",
            "hero_title": "Short hero title (e.g. Hi, I'm Vasu Chauhan)",
            "hero_subtitle": "Short hero subtitle summarizing core expertise",
            "about_heading": "About Me section heading",
            "about_text": "Extracted about me summary or paragraph",
            "skills": [
                {{"name": "Skill Name", "percentage": 0 to 100, "order": index}}
            ],
            "projects": [
                {{"title": "Project Title", "description": "Short description of project", "tech": "Languages/Tools used (comma separated)", "impact": "Core impact or feature", "order": index}}
            ],
            "experiences": [
                {{"company": "Company Name", "role": "Job Role/Title", "description": "Job duties and achievements", "start_date": "Date", "end_date": "Date", "order": index}}
            ],
            "educations": [
                {{"institution": "School/College Name", "degree": "Degree and Major", "description": "Details (GPA, coursework, activities)", "start_date": "Date", "end_date": "Date", "order": index}}
            ],
            "achievements": [
                {{"title": "Achievement Title", "description": "Description of achievement", "date": "Date", "order": index}}
            ]
        }}
        """
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean potential markdown output
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        data = json.loads(response_text)
        
        # Populate Profile core details if matching name
        if data.get("name"):
            profile_obj.name = data.get("name")
        if data.get("hero_title"):
            profile_obj.hero_title = data.get("hero_title")
        if data.get("hero_subtitle"):
            profile_obj.hero_subtitle = data.get("hero_subtitle")
        if data.get("about_heading"):
            profile_obj.about_heading = data.get("about_heading")
        if data.get("about_text"):
            profile_obj.about_text = data.get("about_text")
            
        # Recreate Skills
        if data.get("skills"):
            Skill.objects.all().delete()
            for s in data["skills"]:
                Skill.objects.create(
                    name=s.get("name"),
                    percentage=s.get("percentage", 50),
                    order=s.get("order", 0)
                )
                
        # Recreate Projects
        if data.get("projects"):
            Project.objects.all().delete()
            for p in data["projects"]:
                Project.objects.create(
                    title=p.get("title"),
                    description=p.get("description"),
                    tech=p.get("tech", ""),
                    impact=p.get("impact", ""),
                    order=p.get("order", 0)
                )
                
        # Recreate Experiences
        if data.get("experiences"):
            Experience.objects.all().delete()
            for e in data["experiences"]:
                Experience.objects.create(
                    company=e.get("company"),
                    role=e.get("role"),
                    description=e.get("description"),
                    start_date=e.get("start_date", ""),
                    end_date=e.get("end_date", ""),
                    order=e.get("order", 0)
                )
                
        # Recreate Educations
        if data.get("educations"):
            Education.objects.all().delete()
            for ed in data["educations"]:
                Education.objects.create(
                    institution=ed.get("institution"),
                    degree=ed.get("degree"),
                    description=ed.get("description", ""),
                    start_date=ed.get("start_date", ""),
                    end_date=ed.get("end_date", ""),
                    order=ed.get("order", 0)
                )
                
        # Recreate Achievements
        if data.get("achievements"):
            Achievement.objects.all().delete()
            for a in data["achievements"]:
                Achievement.objects.create(
                    title=a.get("title"),
                    description=a.get("description"),
                    date=a.get("date", ""),
                    order=a.get("order", 0)
                )
                
        if request:
            messages.success(request, "Successfully parsed CV and populated portfolio database fields!")
            
    except Exception as e:
        print("Gemini parsing failed:", e)
        if request:
            messages.error(request, f"Gemini database population failed: {str(e)}")


class ProfileAdminForm(forms.ModelForm):
    about_image_file = forms.ImageField(required=False, label="Upload About Image")
    cv_file_upload = forms.FileField(required=False, label="Upload CV File (PDF)")

    class Meta:
        model = Profile
        fields = '__all__'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = ('name', 'hero_title')
    search_fields = ('name', 'about_text')
    actions = ['parse_cv_action']

    def save_model(self, request, obj, form, change):
        # 1. Upload new about image to Cloudinary if supplied
        about_img_file = form.cleaned_data.get('about_image_file')
        if about_img_file:
            url = upload_to_cloudinary(about_img_file, 'profile')
            if url:
                obj.about_image = url

        # 2. Upload new CV file to Cloudinary if supplied
        cv_file_upload = form.cleaned_data.get('cv_file_upload')
        extracted_text = ""
        
        if cv_file_upload:
            # Upload to Cloudinary
            url = upload_to_cloudinary(cv_file_upload, 'cv')
            if url:
                obj.cv_file = url
            # Extract text from memory stream
            try:
                cv_file_upload.seek(0)
                extracted_text = extract_text_from_pdf(cv_file_upload)
            except Exception as e:
                print("Failed to seek or read uploaded file:", e)
        elif obj.cv_file and obj.cv_file.startswith('http'):
            # Fetch remote PDF and extract text
            try:
                response = requests.get(obj.cv_file)
                if response.status_code == 200:
                    pdf_stream = io.BytesIO(response.content)
                    extracted_text = extract_text_from_pdf(pdf_stream)
            except Exception as e:
                print("Failed to download remote CV file:", e)

        # 3. Store extracted CV text
        if extracted_text:
            obj.cv_text = extracted_text

        # 4. Save model to database
        super().save_model(request, obj, form, change)

        # 5. Populate portfolio database fields using Gemini if CV text was retrieved
        if extracted_text:
            run_gemini_population(obj, extracted_text, request)

    def parse_cv_action(self, request, queryset):
        """Action button to trigger parsing on an existing profile object."""
        for profile in queryset:
            if profile.cv_text:
                run_gemini_population(profile, profile.cv_text, request)
                profile.save()
            else:
                messages.warning(request, f"Profile '{profile.name}' has no CV text to parse.")
    parse_cv_action.short_description = "Repopulate portfolio database fields from CV"


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage', 'order')
    search_fields = ('name',)
    list_editable = ('percentage', 'order')


class ProjectAdminForm(forms.ModelForm):
    project_image_file = forms.ImageField(required=False, label="Upload Project Image")

    class Meta:
        model = Project
        fields = '__all__'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ('title', 'order')
    search_fields = ('title', 'description')
    list_editable = ('order',)

    def save_model(self, request, obj, form, change):
        img_file = form.cleaned_data.get('project_image_file')
        if img_file:
            url = upload_to_cloudinary(img_file, 'projects')
            if url:
                obj.image = url
        super().save_model(request, obj, form, change)


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'visited_at', 'path')
    readonly_fields = ('ip_address', 'user_agent', 'visited_at', 'path')

    def has_add_permission(self, request):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    readonly_fields = ('name', 'email', 'message', 'created_at')
    search_fields = ('name', 'email', 'message')
    list_filter = ('created_at',)

    def has_add_permission(self, request):
        return False


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('role', 'company', 'start_date', 'end_date', 'order')
    list_editable = ('order',)
    search_fields = ('role', 'company', 'description')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'institution', 'start_date', 'end_date', 'order')
    list_editable = ('order',)
    search_fields = ('degree', 'institution', 'description')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'description')
