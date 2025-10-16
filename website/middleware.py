from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class AdminAccessMiddleware:
    """
    Middleware لحماية الوصول للمناطق الإدارية
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # قائمة المسارات المحمية
        protected_paths = [
            '/admin/',
            '/dashboard/',
        ]
        
        # التحقق من المسار
        if any(request.path.startswith(path) for path in protected_paths):
            # إذا كان المستخدم غير مسجل دخول
            if not request.user.is_authenticated:
                messages.error(request, 'يجب تسجيل الدخول للوصول لهذه الصفحة')
                return redirect('login')
            
            # إذا كان المستخدم ليس مشرف
            if not request.user.is_superuser:
                messages.error(request, 'ليس لديك صلاحية للوصول لهذه الصفحة')
                return redirect('home')
        
        response = self.get_response(request)
        return response

