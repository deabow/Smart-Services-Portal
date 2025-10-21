from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from requests_app.models import Request, RequestStatus

User = get_user_model()

class Command(BaseCommand):
    help = 'إنشاء بيانات تجريبية للطلبات'

    def handle(self, *args, **options):
        # إنشاء حالات الطلبات
        statuses = [
            "قيد المراجعة",
            "قيد المعالجة", 
            "مكتمل",
            "مرفوض"
        ]
        
        for status_name in statuses:
            status, created = RequestStatus.objects.get_or_create(name=status_name)
            if created:
                self.stdout.write(f'تم إنشاء حالة: {status_name}')
        
        # إنشاء مستخدم تجريبي إذا لم يكن موجود
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'مستخدم',
                'last_name': 'تجريبي'
            }
        )
        if created:
            user.set_password('test123')
            user.save()
            self.stdout.write('تم إنشاء مستخدم تجريبي')
        
        # إنشاء طلبات تجريبية
        sample_requests = [
            {
                'title': 'طلب إصلاح شارع',
                'description': 'أحتاج إصلاح شارع في منطقتي لأنه مليء بالحفر',
                'full_name': 'أحمد محمد علي',
                'phone': '0123456789',
                'address': 'شارع السلام - السادات'
            },
            {
                'title': 'طلب إنارة',
                'description': 'الشارع مظلم ليلاً ويحتاج إنارة',
                'full_name': 'فاطمة أحمد',
                'phone': '0987654321', 
                'address': 'شارع النور - منوف'
            },
            {
                'title': 'طلب صرف صحي',
                'description': 'مشكلة في الصرف الصحي في المنطقة',
                'full_name': 'محمد علي حسن',
                'phone': '0555666777',
                'address': 'شارع الهدى - سرس الليان'
            }
        ]
        
        statuses_list = list(RequestStatus.objects.all())
        
        for i, request_data in enumerate(sample_requests):
            request_obj, created = Request.objects.get_or_create(
                title=request_data['title'],
                user=user,
                defaults={
                    'description': request_data['description'],
                    'full_name': request_data['full_name'],
                    'phone': request_data['phone'],
                    'address': request_data['address'],
                    'status': statuses_list[i % len(statuses_list)]
                }
            )
            if created:
                self.stdout.write(f'تم إنشاء طلب: {request_data["title"]}')
        
        self.stdout.write(
            self.style.SUCCESS('تم إنشاء البيانات التجريبية بنجاح!')
        ) 