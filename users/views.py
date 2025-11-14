from __future__ import annotations

from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import generics, permissions

from .models import PasswordResetRequest
from .serializers import RegisterSerializer, UserSerializer


User = get_user_model()


class RegisterView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = RegisterSerializer
	permission_classes = [permissions.AllowAny]


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
	if request.method == "POST":
		user = request.user
		user.full_name = request.POST.get("full_name", user.full_name)
		user.phone = request.POST.get("phone", user.phone)
		user.address = request.POST.get("address", user.address)
		user.save()
		return redirect("users:profile")
	return render(request, "users/profile.html")


def signup_page(request: HttpRequest) -> HttpResponse:
	if request.method == "POST":
		username = request.POST.get("username")
		email = request.POST.get("email")
		password1 = request.POST.get("password1")
		password2 = request.POST.get("password2")
		full_name = request.POST.get("full_name", "")
		phone = request.POST.get("phone", "")
		address = request.POST.get("address", "")
		national_id = request.POST.get("national_id", "")
		
		# التحقق من صحة البيانات
		errors = []
		
		if not username:
			errors.append("اسم المستخدم مطلوب")
		if not email:
			errors.append("البريد الإلكتروني مطلوب")
		if not password1:
			errors.append("كلمة المرور مطلوبة")
		if password1 != password2:
			errors.append("كلمتا المرور غير متطابقتين")
		if not phone:
			errors.append("رقم الهاتف مطلوب")
		elif not phone.isdigit() or len(phone) < 10 or len(phone) > 11:
			errors.append("رقم الهاتف يجب أن يكون من 10-11 رقم")
		if not address:
			errors.append("العنوان مطلوب")
		if not national_id:
			errors.append("الرقم القومي مطلوب")
		elif not national_id.isdigit() or len(national_id) != 14:
			errors.append("الرقم القومي يجب أن يكون 14 رقم")
		
		# التحقق من وجود المستخدم
		if User.objects.filter(username=username).exists():
			errors.append("اسم المستخدم موجود بالفعل")
		if User.objects.filter(email=email).exists():
			errors.append("البريد الإلكتروني موجود بالفعل")
		if national_id and User.objects.filter(national_id=national_id).exists():
			errors.append("الرقم القومي مسجل بالفعل")
		
		if errors:
			# إرجاع الأخطاء للقالب
			context = {
				'errors': errors,
				'form_data': request.POST
			}
			return render(request, "users/signup.html", context)
		
		# إنشاء المستخدم
		try:
			user = User.objects.create_user(
				username=username,
				email=email,
				password=password1,
				full_name=full_name,
				phone=phone,
				address=address,
				national_id=national_id
			)
			login(request, user)
			return redirect("home")
		except Exception as e:
			context = {
				'errors': [f"حدث خطأ أثناء إنشاء الحساب: {str(e)}"],
				'form_data': request.POST
			}
			return render(request, "users/signup.html", context)
	
	return render(request, "users/signup.html")


def logout_view(request: HttpRequest) -> HttpResponse:
	if request.method == 'POST':
		logout(request)
		return redirect("home")
	return render(request, 'registration/logout.html')


def password_reset_request_view(request: HttpRequest) -> HttpResponse:
	"""عرض لطلب استعادة كلمة المرور من المشرف"""
	if request.method == 'POST':
		username = request.POST.get('username')
		national_id = request.POST.get('national_id')
		phone = request.POST.get('phone')
		reason = request.POST.get('reason', '')
		
		errors = []
		
		# التحقق من البيانات
		if not username:
			errors.append("اسم المستخدم مطلوب")
		if not national_id:
			errors.append("الرقم القومي مطلوب")
		elif not national_id.isdigit() or len(national_id) != 14:
			errors.append("الرقم القومي يجب أن يكون 14 رقم")
		if not phone:
			errors.append("رقم الهاتف مطلوب")
		elif not phone.isdigit() or len(phone) < 10 or len(phone) > 11:
			errors.append("رقم الهاتف يجب أن يكون من 10-11 رقم")
		
		if errors:
			return render(request, 'users/password_reset_request.html', {
				'errors': errors,
				'form_data': request.POST
			})
		
		# التحقق من المستخدم والبيانات
		try:
			user = User.objects.get(username=username)
			
			# التحقق من الرقم القومي ورقم الهاتف
			if user.national_id != national_id:
				errors.append("الرقم القومي غير متطابق مع الحساب")
			if user.phone != phone:
				errors.append("رقم الهاتف غير متطابق مع الحساب")
			
			if errors:
				return render(request, 'users/password_reset_request.html', {
					'errors': errors,
					'form_data': request.POST
				})
			
			# التحقق من وجود طلب معلق بالفعل
			existing_request = PasswordResetRequest.objects.filter(
				user=user,
				status='pending'
			).first()
			
			if existing_request:
				messages.warning(request, "يوجد طلب معلق بالفعل. سيتم مراجعة طلبك قريباً.")
				return redirect('users:password_reset_request')
			
			# إنشاء طلب جديد
			PasswordResetRequest.objects.create(
				user=user,
				national_id=national_id,
				phone=phone,
				reason=reason
			)
			
			messages.success(request, "تم إرسال طلبك بنجاح. سيتم مراجعة طلبك من قبل الإدارة قريباً.")
			return redirect('users:password_reset_request')
			
		except User.DoesNotExist:
			errors.append("اسم المستخدم غير موجود")
			return render(request, 'users/password_reset_request.html', {
				'errors': errors,
				'form_data': request.POST
			})
	
	return render(request, 'users/password_reset_request.html')


@staff_member_required
def password_reset_admin_view(request: HttpRequest) -> HttpResponse:
	"""عرض للمشرف لإدارة طلبات استعادة كلمة المرور"""
	requests = PasswordResetRequest.objects.select_related('user', 'admin_user').all()
	
	# فلترة حسب الحالة
	status_filter = request.GET.get('status', '')
	if status_filter:
		requests = requests.filter(status=status_filter)
	
	# إحصائيات
	stats = {
		'total': PasswordResetRequest.objects.count(),
		'pending': PasswordResetRequest.objects.filter(status='pending').count(),
		'approved': PasswordResetRequest.objects.filter(status='approved').count(),
		'rejected': PasswordResetRequest.objects.filter(status='rejected').count(),
		'completed': PasswordResetRequest.objects.filter(status='completed').count(),
	}
	
	return render(request, 'users/password_reset_admin.html', {
		'requests': requests,
		'stats': stats,
		'current_status': status_filter,
	})


@staff_member_required
def password_reset_admin_handle_view(request: HttpRequest, request_id: int) -> HttpResponse:
	"""معالجة طلب استعادة كلمة المرور"""
	reset_request = get_object_or_404(PasswordResetRequest, id=request_id)
	
	if request.method == 'POST':
		action = request.POST.get('action')
		notes = request.POST.get('notes', '')
		
		if action == 'approve':
			reset_request.approve(request.user, notes)
			messages.success(request, f"تم الموافقة على طلب {reset_request.user.username}")
		elif action == 'reject':
			reset_request.reject(request.user, notes)
			messages.success(request, f"تم رفض طلب {reset_request.user.username}")
		elif action == 'complete':
			# إعادة تعيين كلمة المرور
			new_password = request.POST.get('new_password')
			if new_password:
				reset_request.user.set_password(new_password)
				reset_request.user.save()
				reset_request.complete(request.user, notes)
				messages.success(request, f"تم إعادة تعيين كلمة المرور لـ {reset_request.user.username}")
			else:
				messages.error(request, "يجب إدخال كلمة مرور جديدة")
		elif action == 'reset_password':
			# إعادة تعيين كلمة المرور فقط
			new_password = request.POST.get('new_password')
			if new_password:
				reset_request.user.set_password(new_password)
				reset_request.user.save()
				messages.success(request, f"تم إعادة تعيين كلمة المرور لـ {reset_request.user.username}")
			else:
				messages.error(request, "يجب إدخال كلمة مرور جديدة")
		
		return redirect('users:password_reset_admin_handle', request_id=request_id)
	
	return render(request, 'users/password_reset_admin_handle.html', {
		'reset_request': reset_request,
	})
