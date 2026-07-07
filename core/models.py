from django.db import models


class Profile(models.Model):
    name = models.CharField(max_length=100, default="Your Name")
    hero_title = models.CharField(max_length=200, default="Hi, I'm [Your Name]")
    hero_subtitle = models.CharField(max_length=300, default="I build things for the web.")
    about_heading = models.CharField(max_length=200, default="About Me")
    about_text = models.TextField()
    about_image = models.TextField(blank=True, default='')
    cv_file = models.TextField(blank=True, default='', help_text='Cloudinary URL of uploaded CV')
    cv_text = models.TextField(blank=True, default='', help_text='Parsed text content from CV PDF')
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


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} ({self.email}) on {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Experience(models.Model):
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.CharField(max_length=50, help_text="e.g., June 2024")
    end_date = models.CharField(max_length=50, help_text="e.g., Present or August 2024")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']

    def __str__(self):
        return f"{self.role} at {self.company}"


class Education(models.Model):
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    start_date = models.CharField(max_length=50, help_text="e.g., 2021")
    end_date = models.CharField(max_length=50, help_text="e.g., 2025")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']

    def __str__(self):
        return f"{self.degree} at {self.institution}"


class Achievement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.CharField(max_length=100, blank=True, default='')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title
