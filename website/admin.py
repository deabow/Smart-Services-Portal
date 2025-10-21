from django.contrib import admin
from django.contrib.auth.models import Group

# إزالة نموذج المجموعات الافتراضي
admin.site.unregister(Group)

# تخصيص عنوان لوحة الإدارة
admin.site.site_header = "لوحة إدارة خدمة المواطنين"
admin.site.site_title = "إدارة خدمة المواطنين"
admin.site.index_title = "مرحباً بك في لوحة إدارة خدمة المواطنين" 