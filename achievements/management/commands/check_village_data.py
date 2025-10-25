from django.core.management.base import BaseCommand
from achievements.models import Achievement, VILLAGES
import json

class Command(BaseCommand):
    help = 'Check village data in database'

    def handle(self, *args, **options):
        # Create a report dictionary
        report = {
            'available_villages': {},
            'village_stats': {},
            'invalid_villages': [],
            'potential_fixes': []
        }
        
        # Show all available villages in each area
        for area, villages in VILLAGES.items():
            report['available_villages'][area] = [v[0] for v in villages]
        
        # Statistics of villages used in database
        for achievement in Achievement.objects.all():
            if achievement.village:
                village = achievement.village
                if village not in report['village_stats']:
                    report['village_stats'][village] = 0
                report['village_stats'][village] += 1
                
                # Check if village is valid
                area_villages = [v[0] for v in VILLAGES.get(achievement.area, [])]
                if village not in area_villages:
                    report['invalid_villages'].append({
                        'id': achievement.id,
                        'title': achievement.title,
                        'area': achievement.area,
                        'village': village
                    })
        
        # Search for specific issue
        for achievement in Achievement.objects.all():
            if achievement.village == 'هيت':
                report['potential_fixes'].append({
                    'id': achievement.id,
                    'title': achievement.title,
                    'area': achievement.area
                })
        
        # Save report to file
        with open('village_data_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.stdout.write('Report saved to village_data_report.json')
        self.stdout.write(f'Total achievements: {Achievement.objects.count()}')
        self.stdout.write(f'Invalid villages: {len(report["invalid_villages"])}')
        self.stdout.write(f'Potential fixes: {len(report["potential_fixes"])}')