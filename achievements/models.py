from __future__ import annotations

from django.db import models


AREAS = (
	("السادات", "السادات"),
	("منوف", "منوف"),
	("سرس الليان", "سرس الليان"),
)

VILLAGES = {
	"منوف": [
		("مدينة منوف", "مدينة منوف"),
		("طملاي", "طملاي"),
		("شبشير طملاي", "شبشير طملاي"),
		("برهيم و منشأة سدود", "برهيم و منشأة سدود"),
		("جزي", "جزي"),
		("منشأة غمرين", "منشأة غمرين"),
		("بالمشط", "بالمشط"),
		("كفر السنابسه", "كفر السنابسه"),
		("صنصفط", "صنصفط"),
		("دمليج", "دمليج"),
		("زاوية رزين", "زاوية رزين"),
		("سدود", "سدود"),
		("بهواش", "بهواش"),
		("كمشوش", "كمشوش"),
		("فيشا الكبري", "فيشا الكبري"),
		("كفر فيشا الكبري", "كفر فيشا الكبري"),
		("هيت", "هيت"),
		("سروهيت", "سروهيت"),
		("دبركي", "دبركي"),
		("غمرين", "غمرين"),
		("تتا", "تتا"),
		("منشأة سلطان", "منشأة سلطان"),
		("سنجرج", "سنجرج"),
		("شبرا بلوله", "شبرا بلوله"),
		("كفر شبرا بلوله", "كفر شبرا بلوله"),
		("الحامول", "الحامول"),
		("كفر العامره", "كفر العامره"),
		("كفر رماح", "كفر رماح"),
		("ميت ربيعه", "ميت ربيعه"),
	],
	"السادات": [
		("مدينة السادات", "مدينة السادات"),
		("كفر داوود", "كفر داوود"),
		("السلام", "السلام"),
		("الطرانه", "الطرانه"),
		("الاخماس", "الاخماس"),
		("الجيار", "الجيار"),
		("الخطاطبة البلد", "الخطاطبة البلد"),
		("الخطاطبة المحطه", "الخطاطبة المحطه"),
		("ابو نشابه", "ابو نشابه"),
		("عدنان المدني", "عدنان المدني"),
	],
	"سرس الليان": [
		("سرس الليان", "سرس الليان"),
	],
}

# Create a flat list of all villages for choices
ALL_VILLAGES = []
for area_villages in VILLAGES.values():
    ALL_VILLAGES.extend(area_villages)


class Achievement(models.Model):
	title = models.CharField(max_length=255, db_index=True)  # Index for faster searches
	description = models.TextField()
	area = models.CharField(max_length=50, choices=AREAS, db_index=True)  # Index for filtering
	village = models.CharField(max_length=100, choices=ALL_VILLAGES, blank=True, null=True, db_index=True)  # Index for filtering
	created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Index for ordering

	class Meta:
		indexes = [
			models.Index(fields=['area', 'village']),  # Composite index for area+village filtering
			models.Index(fields=['-created_at']),  # Index for ordering by creation date
		]
		ordering = ['-created_at']  # Default ordering

	def __str__(self) -> str:
		return self.title

	@property
	def village_choices(self):
		"""Return available villages for the selected area"""
		return VILLAGES.get(self.area, [])
	
	@property
	def village_display_name(self):
		"""Return the display name of the village"""
		if self.village:
			# Find the display name from choices
			for code, name in ALL_VILLAGES:
				if code == self.village:
					return name
			# If not found in choices, return the village code itself
			return self.village
		return ""


class AchievementImage(models.Model):
	achievement = models.ForeignKey(
		Achievement,
		on_delete=models.CASCADE,
		related_name="images",
	)
	image = models.ImageField(
		upload_to="achievements/%Y/%m/%d/", 
		blank=True, 
		null=True,
		help_text="سيتم تحسين الصورة تلقائياً"
	)
	created_at = models.DateTimeField(auto_now_add=True, db_index=True)

	class Meta:
		ordering = ['created_at']
		indexes = [
			models.Index(fields=['achievement', 'created_at']),
		]

	def __str__(self) -> str:
		return f"Image for {self.achievement_id}"
	
	@property
	def image_url(self):
		"""Return optimized image URL"""
		if self.image:
			return self.image.url
		return None

