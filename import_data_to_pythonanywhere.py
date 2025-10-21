#!/usr/bin/env python
"""
سكريبت لاستيراد البيانات في PythonAnywhere
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
django.setup()

from achievements.models import Achievement, AchievementImage
from users.models import User
from requests_app.models import Request, RequestStatus

def import_achievements(data):
    """استيراد الإنجازات"""
    print("Importing achievements...")
    count = 0
    
    for achievement_data in data['achievements']:
        try:
            achievement = Achievement.objects.create(
                title=achievement_data['title'],
                description=achievement_data['description'],
                area=achievement_data['area'],
                village=achievement_data['village'],
                created_at=achievement_data['created_at']
            )
            count += 1
        except Exception as e:
            print(f"Error creating achievement: {e}")
    
    print(f"Imported {count} achievements")
    return count

def import_achievement_images(data):
    """استيراد صور الإنجازات"""
    print("Importing achievement images...")
    count = 0
    
    for image_data in data['achievement_images']:
        try:
            if image_data['image_path']:
                # البحث عن الإنجاز
                achievement = Achievement.objects.get(title=image_data['achievement_title'])
                AchievementImage.objects.create(
                    achievement=achievement,
                    image=image_data['image_path']
                )
                count += 1
        except Achievement.DoesNotExist:
            print(f"Achievement not found: {image_data['achievement_title']}")
        except Exception as e:
            print(f"Error creating image: {e}")
    
    print(f"Imported {count} images")
    return count

def import_users(data):
    """استيراد المستخدمين"""
    print("Importing users...")
    count = 0
    
    for user_data in data['users']:
        try:
            user = User.objects.create(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_staff=user_data['is_staff'],
                is_superuser=user_data['is_superuser'],
                date_joined=user_data['date_joined']
            )
            count += 1
        except Exception as e:
            print(f"Error creating user: {e}")
    
    print(f"Imported {count} users")
    return count

def import_requests(data):
    """استيراد الطلبات"""
    print("Importing requests...")
    count = 0
    
    for request_data in data['requests']:
        try:
            user = None
            if request_data['user']:
                user = User.objects.get(username=request_data['user'])
            
            status = None
            if request_data['status']:
                status, created = RequestStatus.objects.get_or_create(name=request_data['status'])
            
            request = Request.objects.create(
                title=request_data['title'],
                description=request_data['description'],
                status=status,
                user=user,
                created_at=request_data['created_at']
            )
            count += 1
        except Exception as e:
            print(f"Error creating request: {e}")
    
    print(f"Imported {count} requests")
    return count

def import_all_data(json_file):
    """استيراد جميع البيانات"""
    print(f"Loading data from {json_file}...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Data loaded successfully!")
    print(f"Export date: {data['export_date']}")
    
    # استيراد البيانات
    achievements_count = import_achievements(data)
    images_count = import_achievement_images(data)
    users_count = import_users(data)
    requests_count = import_requests(data)
    
    print(f"\nImport completed!")
    print(f"Imported {achievements_count} achievements")
    print(f"Imported {images_count} images")
    print(f"Imported {users_count} users")
    print(f"Imported {requests_count} requests")
    
    return {
        'achievements': achievements_count,
        'images': images_count,
        'users': users_count,
        'requests': requests_count
    }

if __name__ == "__main__":
    json_file = "database_export_20251018_192323.json"
    
    if not os.path.exists(json_file):
        print(f"File {json_file} not found!")
        print("Please make sure the database export file is in the current directory.")
        sys.exit(1)
    
    print("Starting data import...")
    result = import_all_data(json_file)
    print("Data import completed successfully!")
