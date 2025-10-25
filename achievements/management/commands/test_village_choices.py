from django.core.management.base import BaseCommand
from achievements.models import Achievement, VILLAGES, AREAS

class Command(BaseCommand):
    help = 'Test village choices functionality'

    def handle(self, *args, **options):
        self.stdout.write('Testing village choices functionality...\n')
        
        # Test 1: Check if all areas have valid villages
        self.stdout.write('Test 1: Checking area-village mappings...')
        for area_code, area_name in AREAS:
            villages = VILLAGES.get(area_code, [])
            self.stdout.write(f'Area: {area_code} - {len(villages)} villages')
        
        # Test 2: Check if all achievements have valid area-village combinations
        self.stdout.write('\nTest 2: Checking achievement validity...')
        invalid_count = 0
        
        for achievement in Achievement.objects.all():
            if achievement.village and achievement.area:
                area_villages = [v[0] for v in VILLAGES.get(achievement.area, [])]
                if achievement.village not in area_villages:
                    invalid_count += 1
        
        if invalid_count == 0:
            self.stdout.write('All achievements have valid area-village combinations!')
        else:
            self.stdout.write(f'Found {invalid_count} invalid combinations')
        
        # Test 3: Check village statistics
        self.stdout.write('\nTest 3: Village usage statistics...')
        village_stats = {}
        for achievement in Achievement.objects.all():
            if achievement.village:
                village_stats[achievement.village] = village_stats.get(achievement.village, 0) + 1
        
        self.stdout.write(f'Total villages used: {len(village_stats)}')
        
        self.stdout.write('\nTest completed successfully!')