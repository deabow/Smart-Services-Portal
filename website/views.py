from __future__ import annotations

from django.shortcuts import render

from achievements.models import Achievement
from requests_app.models import Request
from users.models import User


def home_view(request):
    context = {}
    
    # إظهار الإحصائيات فقط للمشرفين
    if request.user.is_authenticated and request.user.is_superuser:
        users_count = User.objects.count()
        completed_requests = Request.objects.filter(status__name="مكتمل").count()
        achievements_count = Achievement.objects.count()
        context.update({
            "users_count": users_count,
            "completed_requests": completed_requests,
            "achievements_count": achievements_count,
            "show_stats": True
        })
    else:
        context["show_stats"] = False
    
    return render(request, "home.html", context)


def about_ahmed_abouzeid_view(request):
    """عرض صفحة عن النائب أحمد أبو زيد"""
    return render(request, "about_ahmed_abouzeid.html")

