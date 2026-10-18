"""
PrintMaster A4 - Configuration Settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Telegram Bot Token
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

# Admin ID (optional - if set, only this Telegram user ID can view /admin /stats)
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()

# Database storage directory
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "printmaster.db"

# Directory to temporarily store user uploaded images
TEMP_DIR = BASE_DIR / "temp_uploads"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Assets directory (supports both standalone folder or full repository)
if (BASE_DIR / "Assets").exists():
    ASSETS_DIR = BASE_DIR / "Assets"
else:
    ASSETS_DIR = BASE_DIR.parent / "Assets"

DEFAULT_SAMPLE_IMAGE = ASSETS_DIR / "sample_image.jpg"
LOGO_BANNER_IMAGE = ASSETS_DIR / "logo_banner.png"
