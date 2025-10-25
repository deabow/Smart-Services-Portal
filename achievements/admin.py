from __future__ import annotations

from django.contrib import admin
from django import forms

from .models import Achievement, AchievementImage, AREAS, VILLAGES


class AchievementAdminForm(forms.ModelForm):
	class Meta:
		model = Achievement
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.instance and self.instance.pk:
			# If editing existing achievement, set initial village choices
			area = self.instance.area
			if area in VILLAGES:
				self.fields['village'].choices = [('', '---------')] + VILLAGES[area]
			else:
				self.fields['village'].choices = [('', '---------')]
		else:
			# If creating new achievement, start with empty village choices
			self.fields['village'].choices = [('', '---------')]
		
		# Add JavaScript to update village choices dynamically
		self.fields['area'].widget.attrs.update({
			'onchange': 'updateVillageChoices(this.value)'
		})

	def clean(self):
		cleaned_data = super().clean()
		area = cleaned_data.get('area')
		village = cleaned_data.get('village')
		
		if area and village:
			# Check if village belongs to selected area
			area_villages = [v[0] for v in VILLAGES.get(area, [])]
			if village not in area_villages:
				raise forms.ValidationError(f"القرية '{village}' لا تنتمي للمركز '{area}'")
		
		return cleaned_data


class AchievementImageInline(admin.TabularInline):
	model = AchievementImage
	extra = 1
	fields = ("image",)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
	form = AchievementAdminForm
	list_display = ("id", "title", "area", "village", "created_at")
	list_display_links = ("title",)
	list_filter = ("area", "village", "created_at")
	search_fields = ("title", "description", "area", "village")
	readonly_fields = ("created_at",)
	fieldsets = (
		("معلومات الإنجاز", {
			"fields": ("title", "description", "area", "village")
		}),
		("التواريخ", {
			"fields": ("created_at",),
			"classes": ("collapse",)
		}),
	)
	inlines = [AchievementImageInline]
	ordering = ("-created_at",)

	def get_form(self, request, obj=None, **kwargs):
		form = super().get_form(request, obj, **kwargs)
		return form

	class Media:
		js = ('admin/js/achievement_admin.js',)
		
	def changelist_view(self, request, extra_context=None):
		extra_context = extra_context or {}
		import json
		extra_context['village_choices'] = json.dumps(VILLAGES, ensure_ascii=False)
		return super().changelist_view(request, extra_context)
		
	def add_view(self, request, form_url='', extra_context=None):
		extra_context = extra_context or {}
		import json
		extra_context['village_choices'] = json.dumps(VILLAGES, ensure_ascii=False)
		return super().add_view(request, form_url, extra_context)
		
	def change_view(self, request, object_id, form_url='', extra_context=None):
		extra_context = extra_context or {}
		import json
		extra_context['village_choices'] = json.dumps(VILLAGES, ensure_ascii=False)
		return super().change_view(request, object_id, form_url, extra_context)

