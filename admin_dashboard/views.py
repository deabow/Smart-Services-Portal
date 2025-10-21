from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from achievements.models import Achievement
from requests_app.models import Request
from users.models import User


@staff_member_required
def dashboard_view(request):
	stats = {
		"users_count": User.objects.count(),
		"requests_count": Request.objects.count(),
		"completed_requests": Request.objects.filter(status__name="مكتمل").count(),
		"achievements_count": Achievement.objects.count(),
	}
	latest_requests = Request.objects.select_related("status", "user").order_by("-created_at")[:10]
	return render(request, "dashboard/index.html", {"stats": stats, "latest_requests": latest_requests})

