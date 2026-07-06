from django.shortcuts import render
from .models import Profile, Skill, Project, Visitor


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def index(request):
    # Log visitor (fail silently if database is read-only, e.g. on serverless Vercel)
    try:
        ip = get_client_ip(request)
        ua = request.META.get('HTTP_USER_AGENT', '')
        Visitor.objects.create(ip_address=ip, user_agent=ua, path=request.path)
    except Exception as e:
        # DB is read-only in production serverless, skip logging
        pass

    profile = Profile.objects.first()
    skills = Skill.objects.all()
    projects = Project.objects.all()
    
    context = {
        'profile': profile,
        'skills': skills,
        'projects': projects,
    }
    return render(request, 'core/index.html', context)


import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import os
from PyPDF2 import PdfReader
import google.generativeai as genai
from django.conf import settings

@csrf_exempt
def chat_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            msg = data.get('message', '').lower()
            profile = Profile.objects.first()
            
            # Extract CV text if exists
            cv_text = ""
            if profile and profile.cv_file:
                try:
                    pdf = PdfReader(profile.cv_file.path)
                    for page in pdf.pages:
                        cv_text += page.extract_text() + "\\n"
                except Exception as e:
                    print("Error reading PDF:", e)

            # Check for API key in settings or environment
            api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
            
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"You are a helpful and professional AI assistant for a portfolio website representing {profile.name if profile else 'a developer'}. Answer the user's message concisely in 1-2 short sentences. Use this CV context if available: '{cv_text}'. User message: '{msg}'"
                response = model.generate_content(prompt)
                reply = response.text
            else:
                reply = "The AI is almost ready! Please paste your API key into `GEMINI_API_KEY` in `my_portfolio/settings.py`."
                
            return JsonResponse({'reply': reply})
        except Exception as e:
            return JsonResponse({'reply': f"Oops, something went wrong: {str(e)}"}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{request.build_absolute_uri('/')}</loc>
        <changefreq>monthly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>'''
    return HttpResponse(sitemap, content_type="application/xml")

