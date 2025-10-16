from django.core.management.base import BaseCommand
from chat_app.models import ChatBotResponse


class Command(BaseCommand):
    help = 'إنشاء ردود البوت الافتراضية'

    def handle(self, *args, **options):
        default_responses = [
            {
                'keyword': 'مرحبا',
                'response': 'مرحباً بك! أنا مساعدك الذكي. كيف يمكنني مساعدتك اليوم؟',
                'action_type': 'info'
            },
            {
                'keyword': 'السلام',
                'response': 'وعليكم السلام! أهلاً وسهلاً بك. كيف يمكنني مساعدتك؟',
                'action_type': 'info'
            },
            {
                'keyword': 'مساعدة',
                'response': 'يمكنني مساعدتك في:\n• تقديم طلبات جديدة\n• متابعة حالة طلباتك\n• الإجابة على استفساراتك\n\nما الذي تحتاج مساعدة فيه؟',
                'action_type': 'help'
            },
            {
                'keyword': 'طلب',
                'response': 'ممتاز! سأساعدك في إنشاء طلب جديد. اشرح لي مشكلتك بالتفصيل وسأقوم بإنشاء طلب رسمي لك.',
                'action_type': 'suggest_request'
            },
            {
                'keyword': 'مشكلة',
                'response': 'أفهم أن لديك مشكلة. اشرح لي تفاصيل المشكلة وسأساعدك في إنشاء طلب لحلها.',
                'action_type': 'suggest_request'
            },
            {
                'keyword': 'شكوى',
                'response': 'أفهم أن لديك شكوى. اشرح لي تفاصيل الشكوى وسأساعدك في تقديمها رسمياً.',
                'action_type': 'suggest_request'
            },
            {
                'keyword': 'حالة',
                'response': 'سأتحقق من حالة طلباتك الآن وأعرض لك آخر التحديثات.',
                'action_type': 'check_status'
            },
            {
                'keyword': 'متابعة',
                'response': 'سأتحقق من حالة طلباتك وأعرض لك آخر التحديثات.',
                'action_type': 'check_status'
            },
            {
                'keyword': 'متى',
                'response': 'سأتحقق من مواعيد طلباتك وأعرض لك آخر التحديثات.',
                'action_type': 'check_status'
            },
            {
                'keyword': 'معلومات',
                'response': 'يمكنني تقديم معلومات عن:\n• الخدمات المتاحة\n• كيفية تقديم الطلبات\n• متابعة حالة الطلبات\n\nما الذي تريد معرفته؟',
                'action_type': 'info'
            }
        ]
        
        created_count = 0
        for response_data in default_responses:
            response, created = ChatBotResponse.objects.get_or_create(
                keyword=response_data['keyword'],
                defaults=response_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'تم إنشاء رد البوت: {response_data["keyword"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'رد البوت موجود بالفعل: {response_data["keyword"]}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'تم إنشاء {created_count} رد جديد للبوت')
        )
