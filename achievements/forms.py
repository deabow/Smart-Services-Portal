from __future__ import annotations

from django import forms
from .models import Achievement, AchievementImage, AREAS, VILLAGES, SECTORS


class AchievementImageForm(forms.ModelForm):
    """نموذج إضافة صورة للإنجاز"""
    
    class Meta:
        model = AchievementImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'image': 'صورة الإنجاز'
        }


class AchievementUpdateForm(forms.ModelForm):
    """نموذج تعديل الإنجاز مع دعم تغيير المركز والقرية"""
    
    sectors = forms.MultipleChoiceField(
        choices=SECTORS,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="القطاعات",
        help_text="اختر قطاع أو أكثر"
    )
    
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'sectors', 'area', 'village']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان الإنجاز'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'وصف الإنجاز'
            }),
            'area': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_area'
            }),
            'village': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_village'
            }),
        }
        labels = {
            'title': 'عنوان الإنجاز',
            'description': 'وصف الإنجاز',
            'area': 'المركز',
            'village': 'القرية',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تعيين خيارات المركز
        self.fields['area'].choices = [('', 'اختر المركز')] + list(AREAS)
        
        # تعيين القطاعات الحالية
        if self.instance and self.instance.pk and self.instance.sectors:
            self.fields['sectors'].initial = self.instance.sectors
        
        # تعيين خيارات القرية بناءً على المركز المحدد
        if self.instance and self.instance.pk:
            # إذا كان تعديل إنجاز موجود
            area = self.instance.area
            if area in VILLAGES:
                self.fields['village'].choices = [('', 'اختر القرية')] + VILLAGES[area]
            else:
                self.fields['village'].choices = [('', 'اختر القرية')]
        else:
            # إذا كان إنجاز جديد، ابدأ بجميع القرى المتاحة
            all_villages = []
            for area_villages in VILLAGES.values():
                all_villages.extend(area_villages)
            self.fields['village'].choices = [('', 'اختر القرية')] + all_villages
        
        # إضافة JavaScript لتحديث خيارات القرية ديناميكياً
        self.fields['area'].widget.attrs.update({
            'onchange': 'updateVillageChoices(this.value)'
        })

    def clean_sectors(self):
        """تحويل القطاعات المحددة إلى قائمة"""
        sectors = self.cleaned_data.get('sectors')
        if sectors:
            return list(sectors)
        return []
    
    def save(self, commit=True):
        """حفظ النموذج ومعالجة القطاعات بشكل صحيح"""
        instance = super().save(commit=False)
        # الحصول على بيانات القطاعات المنظفة
        sectors = self.cleaned_data.get('sectors')
        if sectors:
            instance.sectors = list(sectors)
        else:
            instance.sectors = []
        if commit:
            instance.save()
        return instance

    def clean(self):
        """تحقق من صحة البيانات"""
        cleaned_data = super().clean()
        # لا نحتاج للتحقق من القرية هنا لأن JavaScript يتولى المهمة
        return cleaned_data


class AchievementCreateForm(AchievementUpdateForm):
    """نموذج إنشاء إنجاز جديد"""
    pass
