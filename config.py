import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

APP_NAME = "Asfandyar AI Studio"
APP_VERSION = "1.0.0"

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

SECRET_KEY = os.getenv("SECRET_KEY", "")

TIMEZONE = "Asia/Karachi"

# Platform settings
BLOGGER_ENABLED = True
ADSTERRA_ENABLED = True
MONETAG_ENABLED = True

# Social media settings
FACEBOOK_ENABLED = True
X_ENABLED = True
PINTEREST_ENABLED = False

# Free tools only
PAID_SERVICES_ALLOWED = False
