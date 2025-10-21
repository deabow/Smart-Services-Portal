from __future__ import annotations

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from requests_app.models import Request

User = get_user_model()


class ChatRoom(models.Model):
    """غرفة الدردشة - كل مواطن له غرفة واحدة"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="chat_room",
        verbose_name="المستخدم"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "غرفة الدردشة"
        verbose_name_plural = "غرف الدردشة"

    def __str__(self):
        return f"دردشة {self.user.username}"


class Message(models.Model):
    """رسالة في الدردشة"""
    MESSAGE_TYPES = [
        ('user', 'رسالة مستخدم'),
        ('bot', 'رد تلقائي'),
        ('admin', 'رد إداري'),
        ('system', 'رسالة نظام'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(
        ChatRoom, 
        on_delete=models.CASCADE, 
        related_name="messages",
        verbose_name="غرفة الدردشة"
    )
    message_type = models.CharField(
        max_length=10, 
        choices=MESSAGE_TYPES, 
        default='user',
        verbose_name="نوع الرسالة"
    )
    content = models.TextField(verbose_name="محتوى الرسالة")
    is_read = models.BooleanField(default=False, verbose_name="تم القراءة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")

    class Meta:
        verbose_name = "رسالة"
        verbose_name_plural = "الرسائل"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_message_type_display()}: {self.content[:50]}"


class ChatRequest(models.Model):
    """ربط بين الدردشة والطلبات"""
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('created', 'تم الإنشاء'),
        ('rejected', 'مرفوض'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(
        ChatRoom, 
        on_delete=models.CASCADE, 
        related_name="chat_requests",
        verbose_name="غرفة الدردشة"
    )
    request = models.ForeignKey(
        Request, 
        on_delete=models.CASCADE, 
        related_name="chat_requests",
        null=True, 
        blank=True,
        verbose_name="الطلب"
    )
    suggested_title = models.CharField(max_length=200, verbose_name="العنوان المقترح")
    suggested_description = models.TextField(verbose_name="الوصف المقترح")
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name="الحالة"
    )
    user_approved = models.BooleanField(default=False, verbose_name="موافقة المستخدم")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "طلب دردشة"
        verbose_name_plural = "طلبات الدردشة"

    def __str__(self):
        return f"طلب دردشة: {self.suggested_title}"


class ChatBotResponse(models.Model):
    """استجابات البوت الذكي"""
    keyword = models.CharField(max_length=100, verbose_name="الكلمة المفتاحية")
    response = models.TextField(verbose_name="الرد")
    action_type = models.CharField(
        max_length=50, 
        choices=[
            ('info', 'معلومات'),
            ('suggest_request', 'اقتراح طلب'),
            ('check_status', 'فحص حالة'),
            ('help', 'مساعدة'),
        ],
        default='info',
        verbose_name="نوع الإجراء"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    class Meta:
        verbose_name = "رد البوت"
        verbose_name_plural = "ردود البوت"

    def __str__(self):
        return f"{self.keyword}: {self.response[:50]}"


class AdminMessage(models.Model):
    """رسالة إدارية في الدردشة"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(
        ChatRoom, 
        on_delete=models.CASCADE, 
        related_name='admin_messages',
        verbose_name="غرفة الدردشة"
    )
    admin_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="المدير"
    )
    content = models.TextField(verbose_name="محتوى الرسالة")
    message_type = models.CharField(
        max_length=20, 
        choices=[
            ('admin', 'إداري'),
            ('admin_urgent', 'إداري عاجل'),
            ('admin_info', 'معلومات إدارية'),
            ('admin_help', 'مساعدة إدارية')
        ], 
        default='admin', 
        verbose_name="نوع الرسالة"
    )
    is_read_by_user = models.BooleanField(default=False, verbose_name="تم قراءته من المستخدم")
    is_important = models.BooleanField(default=False, verbose_name="مهم")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "رسالة إدارية"
        verbose_name_plural = "الرسائل الإدارية"
        ordering = ['-created_at']

    def __str__(self):
        return f"رسالة إدارية من {self.admin_user.username} في {self.chat_room.user.username}"


class ChatNotification(models.Model):
    """إشعارات الدردشة للإدارة"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(
        ChatRoom, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name="غرفة الدردشة"
    )
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        verbose_name="الرسالة"
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=[
            ('new_message', 'رسالة جديدة'),
            ('urgent_message', 'رسالة عاجلة'),
            ('complaint', 'شكوى'),
            ('request_created', 'طلب جديد'),
            ('user_help', 'طلب مساعدة')
        ], 
        default='new_message', 
        verbose_name="نوع الإشعار"
    )
    is_read = models.BooleanField(default=False, verbose_name="تم القراءة")
    priority = models.IntegerField(default=1, verbose_name="الأولوية")  # 1-10
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "إشعار دردشة"
        verbose_name_plural = "إشعارات الدردشة"
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"إشعار {self.notification_type} من {self.chat_room.user.username}"