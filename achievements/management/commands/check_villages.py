from __future__ import annotations

from django.core.management.base import BaseCommand
from achievements.models import Achievement


class Command(BaseCommand):
    help = "Check current village values in achievements"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Checking village values in achievements..."))
        
        # Get a few achievements to check
        achievements = Achievement.objects.all()[:10]
        
        for achievement in achievements:
            self.stdout.write(f"Title: {achievement.title[:50]}...")
            self.stdout.write(f"  Area: {achievement.area}")
            self.stdout.write(f"  Village (raw): {achievement.village}")
            self.stdout.write(f"  Village (display): {achievement.village_display_name}")
            self.stdout.write("---")
        
        # Show village distribution
        self.stdout.write("\nVillage distribution:")
        from achievements.models import VILLAGES
        
        for area, villages in VILLAGES.items():
            self.stdout.write(f"\n{area}:")
            for code, name in villages:
                count = Achievement.objects.filter(village=code).count()
                if count > 0:
                    self.stdout.write(f"  {code} → {name}: {count} achievements")
