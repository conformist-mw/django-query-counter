from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SECRET_KEY = "key"
DEBUG = True

INSTALLED_APPS = ["app"]

MIDDLEWARE = []

ROOT_URLCONF = "urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}
