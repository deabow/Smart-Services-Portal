from __future__ import annotations

import re
from django.core.management.base import BaseCommand
from django.db import transaction
from achievements.models import Achievement, VILLAGES


class Command(BaseCommand):
    help = "Update existing achievements with village information based on their descriptions"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting village assignment for achievements..."))
        
        updated_count = 0
        not_found_count = 0
        
        # Get all achievements without villages
        achievements = Achievement.objects.filter(village__isnull=True)
        self.stdout.write(f"Found {achievements.count()} achievements without villages")
        
        for achievement in achievements:
            village = self.detect_village_from_description(achievement.description, achievement.area)
            
            if village:
                achievement.village = village
                achievement.save()
                updated_count += 1
                self.stdout.write(f"✓ {achievement.title[:50]}... → {village}")
            else:
                not_found_count += 1
                self.stdout.write(f"✗ {achievement.title[:50]}... → No village found")
        
        self.stdout.write(self.style.SUCCESS(f"\nCompleted! Updated {updated_count} achievements"))
        if not_found_count > 0:
            self.stdout.write(self.style.WARNING(f"{not_found_count} achievements could not be assigned villages"))
    
    def detect_village_from_description(self, description: str, area: str) -> str | None:
        """Detect village from achievement description"""
        if not description or not area:
            return None
        
        # Get villages for this area
        area_villages = VILLAGES.get(area, [])
        if not area_villages:
            return None
        
        # Clean description for better matching
        clean_desc = description.lower().strip()
        
        # Try exact matches first
        for village_code, village_name in area_villages:
            if village_name.lower() in clean_desc:
                return village_code
        
        # Try partial matches for common patterns
        for village_code, village_name in area_villages:
            # Remove common prefixes/suffixes for matching
            clean_village = village_name.lower()
            
            # Handle special cases
            if "كفر" in clean_village:
                # Try with and without "كفر"
                if clean_village in clean_desc or clean_village.replace("كفر ", "") in clean_desc:
                    return village_code
            
            elif "منشأة" in clean_village:
                # Try with and without "منشأة"
                if clean_village in clean_desc or clean_village.replace("منشأة ", "") in clean_desc:
                    return village_code
            
            elif "عزبة" in clean_village:
                # Try with and without "عزبة"
                if clean_village in clean_desc or clean_village.replace("عزبة ", "") in clean_desc:
                    return village_code
            
            else:
                # Regular matching
                if clean_village in clean_desc:
                    return village_code
        
        # Try fuzzy matching for similar names
        for village_code, village_name in area_villages:
            clean_village = village_name.lower()
            
            # Split village name into words and check if most words match
            village_words = clean_village.split()
            desc_words = clean_desc.split()
            
            matches = 0
            for v_word in village_words:
                if any(v_word in d_word for d_word in desc_words):
                    matches += 1
            
            # If more than 50% of words match, consider it a match
            if matches > 0 and matches / len(village_words) >= 0.5:
                return village_code
        
        return None
