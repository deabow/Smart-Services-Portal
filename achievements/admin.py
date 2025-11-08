from __future__ import annotations

from django.contrib import admin
from django import forms
from django.forms.widgets import SelectMultiple

from .models import Achievement, AchievementImage, AREAS, VILLAGES, SECTORS


class FilteredSelectMultiple(SelectMultiple):
	"""Custom widget that looks like filter_horizontal"""
	@property
	def media(self):
		extra = '' if self.allow_multiple_selected else 'admin/js/SelectFilter2.js'
		return forms.Media(
			js=[
				'admin/js/core.js',
				'admin/js/SelectBox.js',
				'admin/js/SelectFilter2.js',
			],
		)
	
	def __init__(self, verbose_name=None, is_stacked=False, attrs=None, choices=()):
		self.verbose_name = verbose_name
		self.is_stacked = is_stacked
		super().__init__(attrs, choices)
	
	def get_context(self, name, value, attrs):
		context = super().get_context(name, value, attrs)
		context['widget']['attrs']['class'] = 'selectfilter'
		if self.is_stacked:
			context['widget']['attrs']['data-field-name'] = self.verbose_name
			context['widget']['attrs']['data-is-stacked'] = '1'
		else:
			context['widget']['attrs']['data-field-name'] = self.verbose_name
			context['widget']['attrs']['data-is-stacked'] = '0'
		return context


class AchievementAdminForm(forms.ModelForm):
	sectors = forms.MultipleChoiceField(
		choices=SECTORS,
		widget=FilteredSelectMultiple(verbose_name='القطاعات', is_stacked=False),
		required=False,
		label="القطاعات",
		help_text="اختر قطاع أو أكثر من القطاعات المتاحة - استخدم الأسهم للنقل بين القوائم"
	)
	
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
			
			# Set initial sectors
			if self.instance.sectors:
				self.fields['sectors'].initial = self.instance.sectors
		else:
			# If creating new achievement, start with all villages available
			all_villages = []
			for area_villages in VILLAGES.values():
				all_villages.extend(area_villages)
			self.fields['village'].choices = [('', '---------')] + all_villages
		
		# Add JavaScript to update village choices dynamically
		self.fields['area'].widget.attrs.update({
			'onchange': 'updateVillageChoices(this.value)'
		})

	def clean_sectors(self):
		"""Convert selected sectors to list"""
		sectors = self.cleaned_data.get('sectors')
		if sectors:
			return list(sectors)
		return []
	
	def save(self, commit=True):
		"""Save the form and properly handle sectors"""
		instance = super().save(commit=False)
		# Get the cleaned sectors data
		sectors = self.cleaned_data.get('sectors')
		if sectors:
			instance.sectors = list(sectors)
		else:
			instance.sectors = []
		if commit:
			instance.save()
		return instance
	
	def clean(self):
		"""Validate the form data"""
		cleaned_data = super().clean()
		# No validation needed here as JavaScript handles the choices
		return cleaned_data


class AchievementImageInline(admin.TabularInline):
	model = AchievementImage
	extra = 1
	fields = ("image",)


class SectorListFilter(admin.SimpleListFilter):
	"""Custom filter for sectors field (JSONField)"""
	title = 'القطاع'  # Display title in sidebar
	parameter_name = 'sector'  # URL parameter
	
	def lookups(self, request, model_admin):
		"""Return list of tuples for filter options"""
		return SECTORS
	
	def queryset(self, request, queryset):
		"""Filter queryset based on selected sector"""
		if self.value():
			# Filter achievements that have this sector in their sectors list
			# Using Python filtering since SQLite doesn't support JSONField contains
			filtered_ids = [
				achievement.id 
				for achievement in queryset 
				if achievement.sectors and self.value() in achievement.sectors
			]
			return queryset.filter(id__in=filtered_ids)
		return queryset


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
	form = AchievementAdminForm
	list_display = ("id", "title", "area", "village", "display_sectors")
	list_display_links = ("title",)
	list_filter = (SectorListFilter, "area", "village")
	search_fields = ("title", "description", "area", "village")
	actions = ['add_to_health', 'add_to_education', 'add_to_youth_sports', 'add_to_roads', 
	           'add_to_infrastructure', 'add_to_agriculture', 'add_to_industry', 'add_to_government_support',
	           'remove_from_sector']
	fieldsets = (
		("معلومات الإنجاز", {
			"fields": ("title", "description", "sectors", "area", "village")
		}),
	)
	
	def display_sectors(self, obj):
		"""Display sectors in list view"""
		if obj.sectors:
			sector_dict = dict(SECTORS)
			sector_names = [sector_dict.get(s, s) for s in obj.sectors]
			return ", ".join(sector_names)
		return "-"
	display_sectors.short_description = "القطاعات"
	
	# Bulk actions for adding to sectors
	def add_to_health(self, request, queryset):
		self._add_to_sector(queryset, 'health', 'الصحي')
		self.message_user(request, f"تم إضافة {queryset.count()} إنجاز إلى قطاع الصحي")
	add_to_health.short_description = "➕ إضافة إلى قطاع الصحي"
	
	def add_to_education(self, request, queryset):
		self._add_to_sector(queryset, 'education', 'التعليم')
		self.message_user(request, f"تم إضافة {queryset.count()} إنجاز إلى قطاع التعليم")
	add_to_education.short_description = "➕ إضافة إلى قطاع التعليم"
	
	def add_to_youth_sports(self, request, queryset):
		self._add_to_sector(queryset, 'youth_sports', 'الشباب والرياضة')
		self.message_user(request, f"تم إضافة {queryset.count()} إنجاز إلى قطاع الشباب والرياضة")
	add_to_youth_sports.short_description = "➕ إضافة إلى قطاع الشباب والرياضة"
	
	def add_to_roads(self, request, queryset):
		self._add_to_sector(queryset, 'roads', 'الطرق')
		self.message_user(request, f"تم إضافة {queryset.count()} إنجاز إلى قطاع الطرق")
	add_to_roads.short_description = "➕ إضافة إلى قطاع الطرق"
	
	def add_to_infrastructure(self, request, queryset):
		self._add_to_sector(queryset, 'infrastructure', 'البنية التحتية')
		self.message_user(request, f"تم إضافة {queryset.count()} إنجاز إلى قطاع البنية التحتية")
	add_to_infrastructure.short_description = "➕ إضافة إلى قطاع البنية التحتية"
	
	def add_to_agriculture(self, request, queryset):
		self._add_to_sector(queryset, 'agriculture', 'الزراعة')
		self.message_user(request, f"تم إضافة {queryset.count()} إنجاز إلى قطاع الزراعة")
	add_to_agriculture.short_description = "➕ إضافة إلى قطاع الزراعة"
	
	def add_to_industry(self, request, queryset):
		self._add_to_sector(queryset, 'industry', 'الصناعة')
		self.message_user(request, f"تم إضافة {queryset.count()} إنجاز إلى قطاع الصناعة")
	add_to_industry.short_description = "➕ إضافة إلى قطاع الصناعة"
	
	def add_to_government_support(self, request, queryset):
		self._add_to_sector(queryset, 'government_support', 'دعم مؤسسات الدولة المصرية')
		self.message_user(request, f"تم إضافة {queryset.count()} إنجاز إلى قطاع دعم مؤسسات الدولة المصرية")
	add_to_government_support.short_description = "➕ إضافة إلى قطاع دعم مؤسسات الدولة"
	
	def remove_from_sector(self, request, queryset):
		"""Remove all sectors from selected achievements"""
		for achievement in queryset:
			achievement.sectors = []
			achievement.save()
		self.message_user(request, f"تم إزالة القطاعات من {queryset.count()} إنجاز")
	remove_from_sector.short_description = "❌ إزالة جميع القطاعات"
	
	def _add_to_sector(self, queryset, sector_code, sector_name):
		"""Helper method to add achievements to a sector"""
		for achievement in queryset:
			if not achievement.sectors:
				achievement.sectors = []
			if sector_code not in achievement.sectors:
				achievement.sectors.append(sector_code)
				achievement.save()
	
	inlines = [AchievementImageInline]
	ordering = ("-id",)

	def get_form(self, request, obj=None, **kwargs):
		form = super().get_form(request, obj, **kwargs)
		return form

	class Media:
		js = ('admin/js/achievement_admin.js',)
		css = {
			'all': ('admin/css/achievement_admin.css',)
		}
		
	def changelist_view(self, request, extra_context=None):
		extra_context = extra_context or {}
		import json
		extra_context['village_choices'] = json.dumps(VILLAGES, ensure_ascii=False)
		extra_context['sector_choices'] = json.dumps(list(SECTORS), ensure_ascii=False)
		return super().changelist_view(request, extra_context)
		
	def add_view(self, request, form_url='', extra_context=None):
		extra_context = extra_context or {}
		import json
		extra_context['village_choices'] = json.dumps(VILLAGES, ensure_ascii=False)
		extra_context['sector_choices'] = json.dumps(list(SECTORS), ensure_ascii=False)
		return super().add_view(request, form_url, extra_context)
		
	def change_view(self, request, object_id, form_url='', extra_context=None):
		extra_context = extra_context or {}
		import json
		extra_context['village_choices'] = json.dumps(VILLAGES, ensure_ascii=False)
		extra_context['sector_choices'] = json.dumps(list(SECTORS), ensure_ascii=False)
		return super().change_view(request, object_id, form_url, extra_context)
