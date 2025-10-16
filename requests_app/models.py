from __future__ import annotations

import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class RequestStatus(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الحالة")
    description = models.TextField(blank=True, verbose_name="وصف الحالة")
    color = models.CharField(max_length=7, default="#6c757d", verbose_name="لون الحالة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "حالة الطلب"
        verbose_name_plural = "حالات الطلبات"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Request(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="requests",
        verbose_name="المستخدم"
    )
    title = models.CharField(max_length=200, verbose_name="عنوان الطلب")
    description = models.TextField(verbose_name="وصف الطلب")
    full_name = models.CharField(max_length=200, verbose_name="الاسم الكامل")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    address = models.TextField(verbose_name="العنوان")
    status = models.ForeignKey(
        RequestStatus, 
        on_delete=models.CASCADE, 
        related_name="requests",
        verbose_name="الحالة"
    )
    tracking_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="رقم التتبع"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.tracking_number}"

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)


class RequestAttachment(models.Model):
    request = models.ForeignKey(
        Request, 
        on_delete=models.CASCADE, 
        related_name="attachments",
        verbose_name="الطلب"
    )
    file_path = models.FileField(
        upload_to="request_attachments/%Y/%m/%d/",
        verbose_name="الملف المرفق"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الرفع")

    class Meta:
        verbose_name = "مرفق الطلب"
        verbose_name_plural = "مرفقات الطلبات"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.request.title} - {self.file_path.name}" 