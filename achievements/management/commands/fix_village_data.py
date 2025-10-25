from django.core.management.base import BaseCommand
from achievements.models import Achievement, VILLAGES
import json

class Command(BaseCommand):
    help = 'Fix village data in database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show proposed changes without applying them',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write('DRY RUN MODE - No changes will be applied')
        
        fixed_count = 0
        area_fixes = 0
        
        # Define correct area-village mappings
        area_village_mapping = {
            'منوف': [
                'مدينة منوف', 'طملاي', 'شبشير طملاي', 'برهيم و منشأة سدود', 'جزي',
                'منشأة غمرين', 'بالمشط', 'كفر السنابسه', 'صنصفط', 'دمليج',
                'زاوية رزين', 'سدود', 'بهواش', 'كمشوش', 'فيشا الكبري',
                'كفر فيشا الكبري', 'هيت', 'سروهيت', 'دبركي', 'غمرين',
                'تتا', 'منشأة سلطان', 'سنجرج', 'شبرا بلوله', 'كفر شبرا بلوله',
                'الحامول', 'كفر العامره', 'كفر رماح', 'ميت ربيعه'
            ],
            'السادات': [
                'مدينة السادات', 'كفر داوود', 'السلام', 'الطرانه', 'الاخماس',
                'الجيار', 'الخطاطبة البلد', 'الخطاطبة المحطه', 'ابو نشابه', 'عدنان المدني'
            ],
            'سرس الليان': [
                'سرس الليان'
            ]
        }
        
        # First, fix the obvious "هيت" to "سروهيت" corrections
        self.stdout.write('Fixing village names...')
        
        for achievement in Achievement.objects.filter(village='هيت'):
            if 'سروهيت' in achievement.title:
                self.stdout.write(f'Fixing achievement {achievement.id}')
                
                if not dry_run:
                    achievement.village = 'سروهيت'
                    achievement.save()
                
                fixed_count += 1
        
        # Fix area-village mismatches
        self.stdout.write('Fixing area-village mismatches...')
        
        for achievement in Achievement.objects.all():
            if achievement.village and achievement.area:
                correct_villages = area_village_mapping.get(achievement.area, [])
                
                if achievement.village not in correct_villages:
                    # Try to find the correct area for this village
                    correct_area = None
                    for area, villages in area_village_mapping.items():
                        if achievement.village in villages:
                            correct_area = area
                            break
                    
                    if correct_area and correct_area != achievement.area:
                        self.stdout.write(
                            f'Fixing area for achievement {achievement.id}'
                        )
                        
                        if not dry_run:
                            achievement.area = correct_area
                            achievement.save()
                        
                        area_fixes += 1
        
        # Summary
        if dry_run:
            self.stdout.write(f'DRY RUN SUMMARY:')
            self.stdout.write(f'Would fix {fixed_count} village names')
            self.stdout.write(f'Would fix {area_fixes} area-village mismatches')
        else:
            self.stdout.write(f'FIX SUMMARY:')
            self.stdout.write(f'Fixed {fixed_count} village names')
            self.stdout.write(f'Fixed {area_fixes} area-village mismatches')
        
        # Generate new report
        self.stdout.write('Generating new report...')
        self.run_check_command()
    
    def run_check_command(self):
        """Run the check command to generate a new report"""
        from django.core.management import call_command
        call_command('check_village_data')