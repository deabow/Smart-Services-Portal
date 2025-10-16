# بوابة خدمات المواطنين — Django 5 + DRF + JWT

هذا المستودع يحتوي على مشروع Django كامل لإدارة:
- المستخدمين وتسجيل الدخول/الخروج
- طلبات المواطنين ومرفقاتهم
- الإنجازات مع صور وفلاتر مناطق
- لوحة تحكم إدارية وإحصاءات
- دردشة بسيطة وإشعارات داخلية

يعتمد المشروع افتراضيًا على قاعدة بيانات SQLite محليًا، ويدعم مصادقة JWT وセ션.

## المتطلبات
- Python 3.11+ على Windows
- PowerShell

## الإعداد السريع على Windows PowerShell
```powershell
cd C:\Users\diabm\Desktop\dipooo
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# تهيئة قاعدة البيانات (SQLite)
python manage.py makemigrations
python manage.py migrate

# إنشاء مستخدم إداري
python manage.py createsuperuser

# تشغيل السيرفر
python manage.py runserver 0.0.0.0:8000
```

بعد التشغيل:
- الواجهة الرئيسية: `/`
- لوحة الإدارة: `/admin/`

## التكوينات الرئيسية (مطابقة للكود الحالي)
- قاعدة البيانات: SQLite في `db.sqlite3` (راجع `website/settings.py`)
- الملفات الثابتة: `static/` أثناء التطوير، و`collectstatic` إلى `staticfiles/`
- ملفات الميديا: `media/`، وتُخدم على `/media/` في وضع التطوير
- مجلد صور عام إضافي: `imgs/` يُخدم على `/imgs/` في وضع التطوير

## التطبيقات والمسارات
- `users`: مسارات حسابات Django القياسية تحت `/accounts/`، ومسارات التطبيق تحت `/users/`
- `requests_app`: تحت `/requests/`
- `achievements`: تحت `/achievements/`
- `admin_dashboard`: تحت `/dashboard/`
- `chat_app`: تحت `/chat/`
- صفحة "عن": `/about/`
- الصفحة الرئيسية: `/`

## مصادقة JWT (DRF SimpleJWT)
- طلب رمز: `POST /api/token/` مع الحقول: `username`, `password`
- تحديث الرمز: `POST /api/token/refresh/` مع `refresh`
- الترويسة: `Authorization: Bearer <access_token>`

## إدارة الإنجازات واستيراد الصور
يوجد أمر إدارة يدعم مصدرين للاستيراد (بالإنجليزية والعربية) كما هو مشار إليه داخل `achievements/management/commands`:
- مجلد `achevments file` ويحتوي `engazat.txt` ومجلد الصور `ENGAZAT`
- مجلد `باقي الانجازات` ويحتوي `باقى الانجازات.txt` ومجلد `الصور الخاصة بالانجازات`

تشغيل الاستيراد من مسار المشروع:
```powershell
python manage.py import_achievements --base .
```

ملاحظة: تم الإبقاء على مجلدات المصدر أعلاه لأنها مستخدمة في أمر الاستيراد.

## التطوير وبناء الملفات الثابتة
أثناء التطوير، تُقرأ الملفات من `static/`. لجمعها للإنتاج:
```powershell
python manage.py collectstatic --noinput
```
سيتم الإخراج إلى `staticfiles/` حسب `STATIC_ROOT`.

## النسخ الاحتياطي وقاعدة البيانات
- الملف `db.sqlite3` هو قاعدة البيانات الحالية.
- توجد نسخ احتياطية مثل `db_backup_YYYY-MM-DD_HH-MM-SS.sqlite3`، يمكنك حذف القديمة إن لم تكن مطلوبة.

## نصائح الشبكة المحلية (LAN)
الإعداد الحالي يسمح بالوصول من أجهزة الشبكة في وضع التطوير (`DEBUG=1`). لتسهيل CSRF على الأجهزة داخل الشبكة، هناك إعدادات تلقائية داخل `website/settings.py`.

## هيكلة المجلدات المهمة
- `website/`: إعدادات المشروع والمسارات والمنظّمات
- `templates/`: القوالب العامة (`base.html`, `home.html`, ...)
- `static/`: CSS/JS/صور الواجهة
- `media/`: مرفقات المستخدمين وصور الإنجازات بعد الرفع
- `imgs/`: صور ثابتة إضافية تخدم عبر `/imgs/` أثناء التطوير
- `users/`, `requests_app/`, `achievements/`, `admin_dashboard/`, `chat_app/`: تطبيقات Django

## أسئلة شائعة
- لا توجد بيانات دخول افتراضية مسبقة. استخدم `createsuperuser` لإنشاء حساب إداري.
- إذا لم تُعرض الصور: تأكد من تشغيل السيرفر في وضع التطوير أو إعداد خادم لإدارة `static` و`media` في الإنتاج.
- مسار `static/images/صورة اللوجو الخاص بالنيف بار.jpg` مستخدم في القوالب وملف `manifest.json` و`sw.js`.

## الترخيص
الاستخدام داخلي للمشروع.