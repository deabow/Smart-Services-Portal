from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Count, Q
from django.conf import settings
import time

from .models import Achievement, AREAS, VILLAGES


def achievements_list_view(request: HttpRequest) -> HttpResponse:
	try:
		area = request.GET.get("area", "").strip()
		village = request.GET.get("village", "").strip()
		
		# Simple query first to ensure it works
		achievements_qs = (
			Achievement.objects
			.prefetch_related("images")
			.order_by("-created_at")
		)
		
		# Apply filters with validation
		if area and area in [a[0] for a in AREAS]:
			achievements_qs = achievements_qs.filter(area=area)
			if village and village in [v[0] for v in VILLAGES.get(area, [])]:
				achievements_qs = achievements_qs.filter(village=village)
		
		# Get available villages for selected area
		available_villages = []
		if area and area in VILLAGES:
			available_villages = VILLAGES[area]
		else:
			# If no area selected, show all villages
			available_villages = []
		
		# Pagination with error handling
		paginator = Paginator(achievements_qs, 12)
		page_number = request.GET.get("page")
		
		try:
			page_obj = paginator.get_page(page_number)
		except Exception as e:
			# If pagination fails, get first page
			page_obj = paginator.get_page(1)
		
		import json
		context = {
			"page_obj": page_obj,
			"areas": AREAS,
			"villages": available_villages,
			"selected_area": area,
			"selected_village": village,
			"village_choices": json.dumps(VILLAGES, ensure_ascii=False),
		}
		
		return render(request, "achievements/list.html", context)
		
	except Exception as e:
		# Log the error for debugging
		import logging
		logger = logging.getLogger(__name__)
		logger.error(f"Error in achievements_list_view: {str(e)}")
		
		# Fallback context in case of any error
		import json
		context = {
			"page_obj": None,
			"areas": AREAS,
			"villages": [],
			"selected_area": None,
			"selected_village": None,
			"village_choices": json.dumps(VILLAGES, ensure_ascii=False),
		}
		return render(request, "achievements/list.html", context)

