from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Count, Q
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import time
import json

from .models import Achievement, AchievementImage, AREAS, VILLAGES
from .forms import AchievementUpdateForm, AchievementCreateForm, AchievementImageForm


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


def achievement_update_view(request: HttpRequest, pk: int) -> HttpResponse:
	"""تعديل إنجاز موجود"""
	achievement = get_object_or_404(Achievement, pk=pk)
	
	if request.method == 'POST':
		form = AchievementUpdateForm(request.POST, instance=achievement)
		if form.is_valid():
			form.save()
			messages.success(request, 'تم تحديث الإنجاز بنجاح!')
			return redirect('achievements:list')
	else:
		form = AchievementUpdateForm(instance=achievement)
	
	import json
	context = {
		'form': form,
		'achievement': achievement,
		'village_choices': json.dumps(VILLAGES, ensure_ascii=False),
	}
	return render(request, 'achievements/update.html', context)


def achievement_create_view(request: HttpRequest) -> HttpResponse:
	"""إنشاء إنجاز جديد"""
	if request.method == 'POST':
		form = AchievementCreateForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'تم إنشاء الإنجاز بنجاح!')
			return redirect('achievements:list')
	else:
		form = AchievementCreateForm()
	
	import json
	context = {
		'form': form,
		'village_choices': json.dumps(VILLAGES, ensure_ascii=False),
	}
	return render(request, 'achievements/create.html', context)


def get_villages_for_area(request: HttpRequest) -> JsonResponse:
	"""API endpoint للحصول على القرى المتاحة لمركز معين"""
	area = request.GET.get('area')
	if area and area in VILLAGES:
		villages = VILLAGES[area]
		return JsonResponse({'villages': villages})
	return JsonResponse({'villages': []})


@require_POST
def add_achievement_image(request: HttpRequest, pk: int) -> JsonResponse:
	"""إضافة صورة للإنجاز"""
	achievement = get_object_or_404(Achievement, pk=pk)
	
	if request.FILES:
		image_file = request.FILES.get('image')
		if image_file:
			# إنشاء صورة جديدة
			achievement_image = AchievementImage.objects.create(
				achievement=achievement,
				image=image_file
			)
			
			return JsonResponse({
				'success': True,
				'message': 'تم رفع الصورة بنجاح',
				'image_id': achievement_image.id,
				'image_url': achievement_image.image.url
			})
	
	return JsonResponse({
		'success': False,
		'message': 'لم يتم رفع أي صورة'
	})


@require_POST
def delete_achievement_image(request: HttpRequest, pk: int) -> JsonResponse:
	"""حذف صورة من الإنجاز"""
	image = get_object_or_404(AchievementImage, pk=pk)
	image.delete()
	
	return JsonResponse({
		'success': True,
		'message': 'تم حذف الصورة بنجاح'
	})


def achievement_images_view(request: HttpRequest, pk: int) -> HttpResponse:
	"""عرض وإدارة صور الإنجاز"""
	achievement = get_object_or_404(Achievement, pk=pk)
	images = achievement.images.all()
	
	context = {
		'achievement': achievement,
		'images': images,
		'image_form': AchievementImageForm()
	}
	return render(request, 'achievements/images.html', context)

