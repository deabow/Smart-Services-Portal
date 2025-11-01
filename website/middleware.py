from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from admin_dashboard.models import SiteVisitor, VisitorStats
from django.utils import timezone


class VisitorTrackingMiddleware:
    """
    Middleware لتتبع زوار الموقع
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # تتبع الزائر
        self.track_visitor(request)
        
        response = self.get_response(request)
        return response
    
    def track_visitor(self, request):
        """تسجيل زيارة جديدة"""
        try:
            # تجاهل طلبات الـ static files و admin static
            if request.path.startswith('/static/') or request.path.startswith('/media/'):
                return
            
            # الحصول على IP address
            ip_address = self.get_client_ip(request)
            
            # الحصول على user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            
            # الحصول على session key
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key or ''
            
            # التحقق من عدم تسجيل نفس الجلسة خلال آخر 30 دقيقة
            recent_visit = SiteVisitor.objects.filter(
                session_key=session_key,
                visit_date__gte=timezone.now() - timezone.timedelta(minutes=30)
            ).exists()
            
            if not recent_visit:
                # تسجيل الزيارة
                SiteVisitor.objects.create(
                    ip_address=ip_address,
                    user_agent=user_agent,
                    user=request.user if request.user.is_authenticated else None,
                    page_visited=request.path,
                    session_key=session_key
                )
                
                # تحديث الإحصائيات اليومية
                VisitorStats.update_today_stats()
            
        except Exception as e:
            # تجاهل الأخطاء لعدم التأثير على تجربة المستخدم
            pass
    
    def get_client_ip(self, request):
        """الحصول على IP address الحقيقي للزائر"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip


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

