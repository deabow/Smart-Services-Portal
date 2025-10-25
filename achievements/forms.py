from __future__ import annotations

from django import forms
from .models import Achievement, AchievementImage, AREAS, VILLAGES


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
    
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'area', 'village']
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
        
        # تعيين خيارات القرية بناءً على المركز المحدد
        if self.instance and self.instance.pk:
            # إذا كان تعديل إنجاز موجود
            area = self.instance.area
            if area in VILLAGES:
                self.fields['village'].choices = [('', 'اختر القرية')] + VILLAGES[area]
            else:
                self.fields['village'].choices = [('', 'اختر القرية')]
        else:
            # إذا كان إنجاز جديد
            self.fields['village'].choices = [('', 'اختر القرية')]
        
        # إضافة JavaScript لتحديث خيارات القرية ديناميكياً
        self.fields['area'].widget.attrs.update({
            'onchange': 'updateVillageChoices(this.value)'
        })

    def clean_village(self):
        """تحقق من صحة القرية المختارة"""
        village = self.cleaned_data.get('village')
        # لا نحتاج للتحقق هنا لأن الخيارات يتم تحديثها ديناميكياً
        return village


class AchievementCreateForm(AchievementUpdateForm):
    """نموذج إنشاء إنجاز جديد"""
    pass
