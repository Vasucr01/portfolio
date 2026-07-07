import os
import json
import io
import requests
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from PyPDF2 import PdfReader
import google.generativeai as genai

from .models import Profile, Skill, Project, Visitor, ContactMessage, Experience, Education, Achievement


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
        print("Visitor log failed:", e)
        pass

    profile = Profile.objects.first()
    skills = Skill.objects.all()
    projects = Project.objects.all()
    experiences = Experience.objects.all()
    educations = Education.objects.all()
    achievements = Achievement.objects.all()

    context = {
        'profile': profile,
        'skills': skills,
        'projects': projects,
        'experiences': experiences,
        'educations': educations,
        'achievements': achievements,
    }
    return render(request, 'core/index.html', context)


@csrf_exempt
def contact_submit(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            message = data.get('message', '').strip()

            if not name or not email or not message:
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            # 1. Save to Database
            msg_obj = ContactMessage.objects.create(name=name, email=email, message=message)

            # 2. Try to Send Email Alert
            try:
                subject = f"Portfolio Message from {name}"
                body = f"You received a new message from your portfolio website:\n\nName: {name}\nEmail: {email}\n\nMessage:\n{message}"
                
                # Check for settings email, default to chauhanvasu01@gmail.com
                admin_email = getattr(settings, 'ADMIN_EMAIL', 'chauhanvasu01@gmail.com')
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@vasuchauhan.me')
                
                send_mail(
                    subject,
                    body,
                    from_email,
                    [admin_email],
                    fail_silently=False,
                )
            except Exception as email_err:
                print("Failed to send contact notification email:", email_err)
                # Fail silently so form response is still success

            return JsonResponse({'reply': 'Message received! Thank you for reaching out.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Invalid method'}, status=405)


def get_chatbot_fallback_reply(msg, profile, skills, projects, experiences, educations, achievements):
    """Fallback rule-based reply when Gemini API is offline/unconfigured."""
    msg = msg.lower()
    
    # 1. AutoFlex
    if "autoflex" in msg or "auto flex" in msg:
        for p in projects:
            if "flex" in p.title.lower():
                return f"AutoFlex is one of Vasu's core projects: {p.description} (Tech: {p.tech}). Impact: {p.impact}"
        return "AutoFlex is a vehicle rental management system featuring automated booking, real-time tracking, digital contracts, and maintenance logs."

    # 2. PathSarthi
    if "pathsarthi" in msg or "path sarthi" in msg:
        for p in projects:
            if "sarthi" in p.title.lower():
                return f"PathSarthi is a project by Vasu: {p.description} (Tech: {p.tech}). Impact: {p.impact}"
        return "PathSarthi is a career guidance and navigation platform for students featuring resume builders, skill assessments, and personalized career roadmaps."

    # 3. SkillNest
    if "skillnest" in msg or "skill nest" in msg:
        for p in projects:
            if "nest" in p.title.lower():
                return f"SkillNest is a project by Vasu: {p.description} (Tech: {p.tech}). Impact: {p.impact}"
        return "SkillNest is a collaborative learning platform enabling peer-to-peer mentoring, group study, and project sharing."

    # 4. Experience / Internship
    if "experience" in msg or "intern" in msg or "work" in msg or "job" in msg:
        if experiences.exists():
            exp_list = [f"{e.role} at {e.company} ({e.start_date} - {e.end_date})" for e in experiences]
            return f"Vasu has professional experience including: {', '.join(exp_list)}. Let me know if you would like details on any role!"
        return "Vasu Chauhan has internship experience as a Python Django developer and IoT system designer. You can find more details in his CV."

    # 5. Projects
    if "projects" in msg or "work examples" in msg or "project list" in msg:
        if projects.exists():
            proj_list = [p.title for p in projects]
            return f"Vasu has built several projects, including: {', '.join(proj_list)}. Ask me about any specific project!"
        return "Vasu's key projects include PathSarthi, AutoFlex, and SkillNest. You can read descriptions for them in the projects section."

    # 6. Skills
    if "skills" in msg or "technolog" in msg or "programming" in msg or "languages" in msg:
        if skills.exists():
            sk_list = [s.name for s in skills]
            return f"Vasu's technical skills include: {', '.join(sk_list)}. He has strong experience in Python, Django, JavaScript, and SQL."
        return "Vasu's key skills include Python, Django, JavaScript, HTML/CSS, SQL, C/Java, and Internet of Things (IoT)."

    # 7. Education / College
    if "education" in msg or "college" in msg or "school" in msg or "study" in msg or "degree" in msg:
        if educations.exists():
            ed_list = [f"{ed.degree} from {ed.institution}" for ed in educations]
            return f"Vasu's education: {', '.join(ed_list)}."
        return "Vasu Chauhan is studying Computer Engineering at V.V.P. Engineering College, Rajkot."

    # 8. Achievements
    if "achievements" in msg or "awards" in msg or "competitions" in msg:
        if achievements.exists():
            ach_list = [a.title for a in achievements]
            return f"Vasu's key achievements: {', '.join(ach_list)}."
        return "Vasu has participated in college hackathons, technical projects, and holds multiple academic and extracurricular achievements."

    # 9. Contact / Hire / Available
    if "contact" in msg or "email" in msg or "hire" in msg or "phone" in msg or "reach" in msg or "available" in msg:
        contact_info = []
        if profile:
            if profile.linkedin_url:
                contact_info.append("LinkedIn")
            if profile.github_url:
                contact_info.append("GitHub")
        channels = f" ({', '.join(contact_info)})" if contact_info else ""
        return f"Vasu is open to internships and full-time roles. You can contact him at chauhanvasu01@gmail.com, use the contact form below, or reach him via his social links{channels}."

    # 10. Resume / CV / Download
    if "resume" in msg or "cv" in msg or "download" in msg:
        if profile and profile.cv_file:
            return f"You can download Vasu's CV directly from this link: {profile.cv_file}"
        return "You can download Vasu's CV by clicking the 'Download CV' button in the header of the page."

    # 11. Who is Vasu / About
    if "who is" in msg or "tell me about" in msg or "about" in msg or "vasu" in msg:
        if profile and profile.about_text:
            return profile.about_text[:300] + "..."
        return "Vasu Chauhan is a motivated Computer Engineering student at V.V.P. Engineering College, Rajkot, specializing in Full-stack Python/Django web development."

    # 12. Default
    return "I'm Vasu's AI assistant. Ask me about his projects (PathSarthi, AutoFlex, SkillNest), skills, education, or check out his download link for his CV!"


@csrf_exempt
def chat_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            msg = data.get('message', '').strip()
            history = data.get('history', [])

            if not msg:
                return JsonResponse({'reply': 'Please type a message.'})

            # Retrieve database objects
            profile = Profile.objects.first()
            skills = Skill.objects.all()
            projects = Project.objects.all()
            experiences = Experience.objects.all()
            educations = Education.objects.all()
            achievements = Achievement.objects.all()

            cv_text = profile.cv_text if (profile and profile.cv_text) else ""

            # Check for API key
            api_key = getattr(settings, 'GEMINI_API_KEY', '')
            import os
            if not api_key:
                api_key = os.environ.get('GEMINI_API_KEY', '')

            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')

                    # Build system instruction / context prompt
                    context_prompt = (
                        f"You are a helpful, professional, and friendly AI assistant representing the developer "
                        f"{profile.name if profile else 'Vasu Chauhan'}. "
                        "Keep your responses concise and engaging (maximum 3-4 sentences). "
                        "Speak directly about Vasu (e.g., use 'Vasu studied...' or 'Vasu's projects are...').\n\n"
                    )

                    if cv_text:
                        context_prompt += f"Here is the CV/Resume context for Vasu:\n{cv_text}\n\n"

                    # Add conversation history
                    history_str = "Conversation history:\n"
                    for chat_turn in history:
                        role = chat_turn.get('role', 'user')
                        text = chat_turn.get('text', '') or chat_turn.get('message', '')
                        speaker = "User" if role == "user" else "AI"
                        history_str += f"{speaker}: {text}\n"

                    # Final prompt
                    final_prompt = f"{context_prompt}{history_str}User: {msg}\nAI:"

                    response = model.generate_content(final_prompt)
                    reply = response.text.strip()
                    return JsonResponse({'reply': reply})

                except Exception as api_err:
                    print("Gemini API call failed, falling back:", api_err)
                    # Proceed to fallback below

            # Fallback when API key is missing or API call fails
            reply = get_chatbot_fallback_reply(
                msg, profile, skills, projects, experiences, educations, achievements
            )
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
