from pathlib import Path

# ریشه‌ی پروژه (یه پله بالاتر از app/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# منابع
RESOURCES_DIR = BASE_DIR / "public"
TEMPLATES_DIR = RESOURCES_DIR / "templates"
STATIC_DIR = RESOURCES_DIR / "resources"

# پوشه‌های static
CSS_DIR = STATIC_DIR / "css"
JS_DIR = STATIC_DIR / "js"
IMAGES_DIR = STATIC_DIR / "images"

# ذخیره‌سازی
STORAGE_DIR = BASE_DIR / "storage"
LOGS_DIR = STORAGE_DIR / "logs"
UPLOADS_DIR = STORAGE_DIR / "uploads"

# اطمینان از وجود پوشه‌ها
for d in (TEMPLATES_DIR, CSS_DIR, JS_DIR, IMAGES_DIR, LOGS_DIR, UPLOADS_DIR):
    d.mkdir(parents=True, exist_ok=True)