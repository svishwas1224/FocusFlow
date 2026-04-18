from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SQLITE_URL = f"sqlite+aiosqlite:///{BASE_DIR / 'focusflow.db'}"

BLOCKED_SITES = [
    "facebook.com",
    "twitter.com",
    "youtube.com",
    "instagram.com",
    "tiktok.com",
]
