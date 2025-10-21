from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import permissions, routers, viewsets

from .models import Request, RequestAttachment, RequestStatus
from .serializers import RequestSerializer


class RequestViewSet(viewsets.ModelViewSet):
	queryset = Request.objects.select_related("status", "user").all()
	serializer_class = RequestSerializer
	permission_classes = [permissions.IsAuthenticated]

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)


router = routers.DefaultRouter()
router.register(r"api", RequestViewSet, basename="request")


@login_required
def request_create_view(request: HttpRequest) -> HttpResponse:
	if request.method == "POST":
		title = request.POST.get("title", "").strip()
		description = request.POST.get("description", "").strip()
		
		# التحقق من صحة البيانات
		errors = []
		
		if not title:
			errors.append("عنوان الطلب مطلوب")
		if not description:
			errors.append("تفاصيل الطلب مطلوبة")
		elif len(description) < 10:
			errors.append("تفاصيل الطلب يجب أن تكون 10 أحرف على الأقل")
		
		if errors:
			context = {
				'errors': errors,
				'form_data': request.POST
			}
			return render(request, "requests/create.html", context)
		
		try:
			# إنشاء حالة الطلب
			status = RequestStatus.objects.get_or_create(name="قيد المراجعة")[0]
			
			# إنشاء الطلب
			req = Request.objects.create(
				user=request.user,
				full_name=request.user.full_name or request.user.username,
				phone=request.user.phone or "",
				address=request.user.address or "",
				title=title,
				description=description,
				status=status,
			)
			
			# إضافة المرفقات
			for f in request.FILES.getlist("attachments"):
				RequestAttachment.objects.create(request=req, file_path=f)
			
			return redirect("requests:list")
			
		except Exception as e:
			context = {
				'errors': [f"حدث خطأ أثناء إنشاء الطلب: {str(e)}"],
				'form_data': request.POST
			}
			return render(request, "requests/create.html", context)
	
	return render(request, "requests/create.html")


@login_required
def request_list_view(request: HttpRequest) -> HttpResponse:
	requests_qs = Request.objects.filter(user=request.user).select_related("status").order_by("-created_at")
	return render(request, "requests/list.html", {"requests": requests_qs})


@login_required
def request_detail_view(request: HttpRequest, tracking_number: str) -> HttpResponse:
	req = get_object_or_404(Request, tracking_number=tracking_number, user=request.user)
	return render(request, "requests/detail.html", {"request_obj": req})

