from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
	full_name = models.CharField(max_length=255, blank=True)
	phone = models.CharField(max_length=20, blank=False, verbose_name="رقم الهاتف")
	address = models.CharField(max_length=255, blank=True)
	national_id = models.CharField(max_length=14, unique=True, null=True, blank=True, verbose_name="الرقم القومي")

	def __str__(self) -> str:  # pragma: no cover - simple display
		return self.username


class PasswordResetRequest(models.Model):
	"""نموذج لطلبات استعادة كلمة المرور من المشرف"""
	
	STATUS_CHOICES = [
		('pending', 'قيد الانتظار'),
		('approved', 'موافق عليه'),
		('rejected', 'مرفوض'),
		('completed', 'مكتمل'),
	]
	
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_requests', verbose_name="المستخدم")
	national_id = models.CharField(max_length=14, verbose_name="الرقم القومي")
	phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
	reason = models.TextField(blank=True, verbose_name="سبب الطلب (اختياري)")
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="الحالة")
	
	# معلومات المشرف
	admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_password_resets', verbose_name="المشرف المعالج")
	admin_notes = models.TextField(blank=True, verbose_name="ملاحظات المشرف")
	
	# التواريخ
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")
	handled_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ المعالجة")
	
	class Meta:
		ordering = ['-created_at']
		verbose_name = "طلب استعادة كلمة المرور"
		verbose_name_plural = "طلبات استعادة كلمة المرور"
		indexes = [
			models.Index(fields=['-created_at']),
			models.Index(fields=['status']),
		]
	
	def __str__(self) -> str:
		return f"طلب استعادة كلمة المرور - {self.user.username} - {self.get_status_display()}"
	
	def approve(self, admin_user, notes=''):
		"""الموافقة على الطلب"""
		self.status = 'approved'
		self.admin_user = admin_user
		self.admin_notes = notes
		self.handled_at = timezone.now()
		self.save()
	
	def reject(self, admin_user, notes=''):
		"""رفض الطلب"""
		self.status = 'rejected'
		self.admin_user = admin_user
		self.admin_notes = notes
		self.handled_at = timezone.now()
		self.save()
	
	def complete(self, admin_user, notes=''):
		"""إكمال الطلب (بعد إعادة تعيين كلمة المرور)"""
		self.status = 'completed'
		self.admin_user = admin_user
		if notes:
			self.admin_notes = notes
		if not self.handled_at:
			self.handled_at = timezone.now()
		self.save()

