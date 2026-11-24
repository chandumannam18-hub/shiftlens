from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "local-workshop-demo-only"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
ROOT_URLCONF = "tracker.urls"
INSTALLED_APPS = ["django.contrib.staticfiles", "tracker"]
STATIC_URL = "/static/"
MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
TIME_ZONE = "Asia/Kolkata"
USE_TZ = True
