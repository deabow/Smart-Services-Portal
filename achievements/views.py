from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator

from .models import Achievement, AREAS, VILLAGES


def achievements_list_view(request: HttpRequest) -> HttpResponse:
	area = request.GET.get("area")
	village = request.GET.get("village")
	
	achievements_qs = (
		Achievement.objects.all()
		.prefetch_related("images")
		.order_by("-created_at")
	)
	
	if area:
		achievements_qs = achievements_qs.filter(area=area)
		if village:
			achievements_qs = achievements_qs.filter(village=village)
	
	# Get available villages for selected area
	available_villages = []
	if area and area in VILLAGES:
		available_villages = VILLAGES[area]
	
	# Paginate results
	paginator = Paginator(achievements_qs, 12)
	page_number = request.GET.get("page")
	page_obj = paginator.get_page(page_number)
	
	context = {
		"page_obj": page_obj,
		"areas": [a for a, _ in AREAS],
		"villages": available_villages,
		"selected_area": area,
		"selected_village": village,
		"village_choices": VILLAGES,
	}
	
	return render(request, "achievements/list.html", context)

