from django.db import models


class Profile(models.Model):
    name = models.CharField(max_length=100, default="Your Name")
    hero_title = models.CharField(max_length=200, default="Hi, I'm [Your Name]")
    hero_subtitle = models.CharField(max_length=300, default="I build things for the web.")
    about_heading = models.CharField(max_length=200, default="About Me")
    about_text = models.TextField()
    # Store Cloudinary URLs directly as text — no local filesystem writes ever
    about_image = models.TextField(blank=True, default='')
    cv_file = models.TextField(blank=True, default='', help_text='Cloudinary URL of uploaded CV')
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.IntegerField(default=50)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-percentage']

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=200)
    # Store Cloudinary URL directly as text
    image = models.TextField(blank=True, default='')
    image_url = models.URLField(blank=True, null=True, help_text="Fallback if no image uploaded")
    description = models.TextField()
    tech = models.CharField(max_length=250)
    impact = models.CharField(max_length=250)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class Visitor(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    visited_at = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-visited_at']

    def __str__(self):
        return f"Visitor from {self.ip_address} on {self.visited_at}"
