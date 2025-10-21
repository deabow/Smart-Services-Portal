from django.core.management.base import BaseCommand
from requests_app.models import RequestStatus


class Command(BaseCommand):
    help = 'إنشاء حالات الطلبات الافتراضية'

    def handle(self, *args, **options):
        statuses = [
            {
                'name': 'تم استلام الطلب',
                'color': '#17a2b8',  # Info color
                'description': 'تم استلام الطلب وسيتم مراجعته'
            },
            {
                'name': 'قيد المراجعة',
                'color': '#ffc107',  # Warning color
                'description': 'الطلب قيد المراجعة من قبل الفريق المختص'
            },
            {
                'name': 'قيد التنفيذ',
                'color': '#007bff',  # Primary color
                'description': 'تم البدء في تنفيذ الطلب'
            },
            {
                'name': 'مكتمل',
                'color': '#28a745',  # Success color
                'description': 'تم إنجاز الطلب بنجاح'
            },
            {
                'name': 'مرفوض',
                'color': '#dc3545',  # Danger color
                'description': 'تم رفض الطلب لعدم توفر المتطلبات'
            },
            {
                'name': 'معلق',
                'color': '#6c757d',  # Secondary color
                'description': 'الطلب معلق بانتظار معلومات إضافية'
            }
        ]

        created_count = 0
        for status_data in statuses:
            status, created = RequestStatus.objects.get_or_create(
                name=status_data['name'],
                defaults={
                    'description': status_data.get('description', ''),
                    'color': status_data.get('color', '#6c757d')
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'تم إنشاء حالة: {status.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'الحالة موجودة بالفعل: {status.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'تم إنشاء {created_count} حالة جديدة')
        )

