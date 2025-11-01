from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class ActivityLog(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
	action = models.CharField(max_length=255)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"{self.user} - {self.action}"


class SiteVisitor(models.Model):
	"""نموذج لتتبع زوار الموقع"""
	ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
	user_agent = models.TextField(blank=True, verbose_name="معلومات المتصفح")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المستخدم")
	visit_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الزيارة")
	page_visited = models.CharField(max_length=500, blank=True, verbose_name="الصفحة المزارة")
	session_key = models.CharField(max_length=100, blank=True, verbose_name="مفتاح الجلسة")
	
	class Meta:
		ordering = ['-visit_date']
		verbose_name = "زائر"
		verbose_name_plural = "الزوار"
		indexes = [
			models.Index(fields=['-visit_date']),
			models.Index(fields=['ip_address']),
			models.Index(fields=['session_key']),
		]
	
	def __str__(self) -> str:
		return f"{self.ip_address} - {self.visit_date.strftime('%Y-%m-%d %H:%M')}"


class VisitorStats(models.Model):
	"""نموذج لحفظ إحصائيات الزوار اليومية"""
	date = models.DateField(unique=True, verbose_name="التاريخ")
	total_visits = models.IntegerField(default=0, verbose_name="إجمالي الزيارات")
	unique_visitors = models.IntegerField(default=0, verbose_name="الزوار الفريدون")
	registered_users = models.IntegerField(default=0, verbose_name="المستخدمون المسجلون")
	guest_visitors = models.IntegerField(default=0, verbose_name="الزوار الضيوف")
	
	class Meta:
		ordering = ['-date']
		verbose_name = "إحصائية يومية"
		verbose_name_plural = "الإحصائيات اليومية"
	
	def __str__(self) -> str:
		return f"{self.date} - {self.total_visits} زيارة"
	
	@classmethod
	def update_today_stats(cls):
		"""تحديث إحصائيات اليوم"""
		today = timezone.now().date()
		today_visits = SiteVisitor.objects.filter(visit_date__date=today)
		
		stats, created = cls.objects.get_or_create(date=today)
		stats.total_visits = today_visits.count()
		stats.unique_visitors = today_visits.values('ip_address').distinct().count()
		stats.registered_users = today_visits.filter(user__isnull=False).values('user').distinct().count()
		stats.guest_visitors = today_visits.filter(user__isnull=True).values('ip_address').distinct().count()
		stats.save()
		return stats

