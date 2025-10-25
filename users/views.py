from __future__ import annotations

from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from rest_framework import generics, permissions

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
		
		# التحقق من وجود المستخدم
		if User.objects.filter(username=username).exists():
			errors.append("اسم المستخدم موجود بالفعل")
		if User.objects.filter(email=email).exists():
			errors.append("البريد الإلكتروني موجود بالفعل")
		
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
				address=address
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
