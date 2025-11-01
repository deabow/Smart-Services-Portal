from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta

from achievements.models import Achievement
from requests_app.models import Request
from users.models import User
from .models import SiteVisitor, VisitorStats


@staff_member_required
def dashboard_view(request):
	# الإحصائيات الأساسية
	stats = {
		"users_count": User.objects.count(),
		"requests_count": Request.objects.count(),
		"completed_requests": Request.objects.filter(status__name="مكتمل").count(),
		"achievements_count": Achievement.objects.count(),
	}
	
	# إحصائيات الزوار
	today = timezone.now().date()
	
	# إحصائيات اليوم
	today_visits = SiteVisitor.objects.filter(visit_date__date=today)
	visitor_stats = {
		"total_visits": SiteVisitor.objects.count(),
		"today_visits": today_visits.count(),
		"today_unique": today_visits.values('ip_address').distinct().count(),
		"today_registered": today_visits.filter(user__isnull=False).values('user').distinct().count(),
		"today_guests": today_visits.filter(user__isnull=True).values('ip_address').distinct().count(),
	}
	
	# إحصائيات آخر 7 أيام
	last_7_days = today - timedelta(days=6)
	weekly_stats = VisitorStats.objects.filter(date__gte=last_7_days).order_by('date')
	
	# إحصائيات آخر 30 يوم
	last_30_days = today - timedelta(days=29)
	monthly_total = SiteVisitor.objects.filter(visit_date__date__gte=last_30_days).count()
	monthly_unique = SiteVisitor.objects.filter(visit_date__date__gte=last_30_days).values('ip_address').distinct().count()
	
	# أحدث الزوار
	recent_visitors = SiteVisitor.objects.select_related('user').order_by('-visit_date')[:20]
	
	latest_requests = Request.objects.select_related("status", "user").order_by("-created_at")[:10]
	
	return render(request, "dashboard/index.html", {
		"stats": stats,
		"visitor_stats": visitor_stats,
		"weekly_stats": weekly_stats,
		"monthly_total": monthly_total,
		"monthly_unique": monthly_unique,
		"recent_visitors": recent_visitors,
		"latest_requests": latest_requests,
	})

