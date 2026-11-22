from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "dev-only-not-a-secret"
DEBUG = True
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth",
                  "django.contrib.staticfiles",
                  "rest_framework", "corsheaders", "reconcile"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware", "django.middleware.common.CommonMiddleware"]
ROOT_URLCONF = "config.urls"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
CORS_ALLOW_ALL_ORIGINS = True  # dev only
REST_FRAMEWORK = {"DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"]}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
STATIC_URL = "static/"