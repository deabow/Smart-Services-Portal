from django.core.management.base import BaseCommand
from django.db import models
from difflib import SequenceMatcher
from achievements.models import Achievement, VILLAGES


class Command(BaseCommand):
    help = 'استخراج أسماء القرى من العناوين والأوصاف وتحديث الإنجازات'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='اختبار النظام على عينة صغيرة فقط',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='عدد الإنجازات المراد معالجتها (افتراضي: 100)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='تشغيل تجريبي بدون حفظ التغييرات',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting village extraction process...'))
        
        # الحصول على جميع أسماء القرى
        all_villages = self.get_all_village_names()
        self.stdout.write(f'Available villages: {len(all_villages)}')
        
        # تحديد الإنجازات المراد معالجتها
        if options['test']:
            achievements = Achievement.objects.filter(
                models.Q(village__isnull=True) | models.Q(village='')
            )[:20]
            self.stdout.write('Test mode: Processing 20 achievements only')
        else:
            achievements = Achievement.objects.filter(
                models.Q(village__isnull=True) | models.Q(village='')
            )[:options['limit']]
            self.stdout.write(f'Processing {len(achievements)} achievements')
        
        # معالجة الإنجازات
        updated_count = 0
        found_count = 0
        
        for achievement in achievements:
            found_village = self.extract_village_from_text(
                achievement.title, 
                achievement.description, 
                all_villages
            )
            
            if found_village:
                found_count += 1
                self.stdout.write(
                    f'ID {achievement.id}: Found village'
                )
                
                if not options['dry_run']:
                    achievement.village = found_village
                    achievement.save()
                    updated_count += 1
                else:
                    self.stdout.write('  (Dry run - not saved)')
        
        # النتائج النهائية
        self.stdout.write(
            self.style.SUCCESS(
                f'\nFinal Results:\n'
                f'- Found villages in {found_count} achievements\n'
                f'- Updated {updated_count} achievements'
            )
        )

    def get_all_village_names(self):
        """الحصول على جميع أسماء القرى"""
        all_villages = []
        for area, villages in VILLAGES.items():
            for village_code, village_name in villages:
                all_villages.append(village_name)
        return all_villages

    def extract_village_from_text(self, title, description, available_villages):
        """
        استخراج اسم القرية من العنوان والوصف
        """
        # البحث في العنوان أولاً
        title_village = self.find_village_in_text(title, available_villages)
        if title_village:
            return title_village
        
        # البحث في الوصف
        desc_village = self.find_village_in_text(description, available_villages)
        if desc_village:
            return desc_village
        
        return None

    def find_village_in_text(self, text, available_villages):
        """
        البحث عن قرية في النص
        """
        if not text:
            return None
        
        text = text.strip()
        best_match = None
        best_score = 0
        
        for village_name in available_villages:
            # البحث المباشر
            if village_name in text:
                return village_name
            
            # البحث بطرق مختلفة
            village_words = village_name.split()
            text_words = text.split()
            
            # البحث عن كلمات متشابهة
            for village_word in village_words:
                for text_word in text_words:
                    similarity = SequenceMatcher(None, village_word, text_word).ratio()
                    if similarity > 0.8 and similarity > best_score:
                        best_score = similarity
                        best_match = village_name
        
        # إذا كان أفضل تطابق جيد جداً، نرجعه
        if best_score > 0.8:
            return best_match
        
        return None
