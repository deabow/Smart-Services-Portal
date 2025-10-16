from __future__ import annotations

from django.core.management.base import BaseCommand
from achievements.models import Achievement, VILLAGES


class Command(BaseCommand):
    help = "Fix village names in existing achievements by mapping them to proper village codes"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting village name fix for achievements..."))
        
        # Create a mapping from display names to codes
        village_mapping = {}
        for area, villages in VILLAGES.items():
            for code, name in villages:
                village_mapping[name] = code
        
        updated_count = 0
        not_found_count = 0
        
        # Get all achievements with villages
        achievements = Achievement.objects.filter(village__isnull=False).exclude(village="")
        self.stdout.write(f"Found {achievements.count()} achievements with villages")
        
        for achievement in achievements:
            current_village = achievement.village
            
            # Check if current village is already a code
            if current_village in [code for code, name in village_mapping.items()]:
                self.stdout.write(f"✓ {achievement.title[:50]}... → Already has correct code: {current_village}")
                continue
            
            # Try to find the village by display name
            if current_village in village_mapping:
                achievement.village = village_mapping[current_village]
                achievement.save()
                updated_count += 1
                self.stdout.write(f"✓ {achievement.title[:50]}... → {current_village} → {village_mapping[current_village]}")
            else:
                not_found_count += 1
                self.stdout.write(f"✗ {achievement.title[:50]}... → Could not map: {current_village}")
        
        self.stdout.write(self.style.SUCCESS(f"\nCompleted! Updated {updated_count} achievements"))
        if not_found_count > 0:
            self.stdout.write(self.style.WARNING(f"{not_found_count} achievements could not be mapped"))
            
        # Show current village distribution
        self.stdout.write("\nCurrent village distribution:")
        for area, villages in VILLAGES.items():
            self.stdout.write(f"\n{area}:")
            for code, name in villages:
                count = Achievement.objects.filter(village=code).count()
                if count > 0:
                    self.stdout.write(f"  {name}: {count} achievements")
