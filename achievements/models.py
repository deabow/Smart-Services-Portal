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
	"سرس الليان": [],
}

# Create a flat list of all villages for choices
ALL_VILLAGES = []
for area_villages in VILLAGES.values():
    ALL_VILLAGES.extend(area_villages)


class Achievement(models.Model):
	title = models.CharField(max_length=255)
	description = models.TextField()
	area = models.CharField(max_length=50, choices=AREAS)
	village = models.CharField(max_length=100, choices=ALL_VILLAGES, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

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
	image = models.ImageField(upload_to="achievements/", blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"Image for {self.achievement_id}"

