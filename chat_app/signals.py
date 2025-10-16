from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatBotResponse

User = get_user_model()


@receiver(post_save, sender=User)
def create_chat_room(sender, instance, created, **kwargs):
    """إنشاء غرفة دردشة تلقائياً عند إنشاء مستخدم جديد"""
    if created:
        ChatRoom.objects.get_or_create(user=instance)


def create_default_bot_responses():
    """إنشاء ردود افتراضية للبوت"""
    default_responses = [
        {
            'keyword': 'مرحبا',
            'response': 'مرحباً بك! أنا مساعدك الذكي. كيف يمكنني مساعدتك اليوم؟',
            'action_type': 'info'
        },
        {
            'keyword': 'مساعدة',
            'response': 'يمكنني مساعدتك في تقديم الطلبات، متابعة حالة طلباتك، والإجابة على استفساراتك.',
            'action_type': 'help'
        },
        {
            'keyword': 'طلب',
            'response': 'ممتاز! سأساعدك في إنشاء طلب جديد. اشرح لي مشكلتك بالتفصيل.',
            'action_type': 'suggest_request'
        },
        {
            'keyword': 'حالة',
            'response': 'سأتحقق من حالة طلباتك الآن.',
            'action_type': 'check_status'
        }
    ]
    
    for response_data in default_responses:
        ChatBotResponse.objects.get_or_create(
            keyword=response_data['keyword'],
            defaults=response_data
        )
