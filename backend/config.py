from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SQLITE_URL = f"sqlite+aiosqlite:///{BASE_DIR / 'focusflow_ai.db'}"

BLOCKED_SITES = [
    "facebook.com",
    "twitter.com",
    "instagram.com",
    "tiktok.com",
    "netflix.com",
]

FORBIDDEN_APPS = [
    "steam",
    "discord",
    "twitch",
    "netflix",
    "reddit",
]

FOCUS_KEYWORDS = [
    "code",
    "visual studio",
    "vscode",
    "pycharm",
    "word",
    "excel",
    "powerpoint",
    "research",
    "report",
    "email",
    "meeting",
    "class",
    "lecture",
    "tutorial",
    "course",
    "study",
    "project",
]

DISTRACTOR_KEYWORDS = [
    "facebook",
    "twitter",
    "instagram",
    "tiktok",
    "netflix",
    "discord",
    "reddit",
    "steam",
    "twitch",
]

FOCUS_CATEGORY_WEIGHTS = {
    "focus": 1.0,
    "neutral": 0.6,
    "distractor": 0.2,
}

POMODORO_SETTINGS = {
    "focus": 25 * 60,
    "short_break": 5 * 60,
    "long_break": 15 * 60,
}

INTERVENTION_THRESHOLD_SCORE = 30
INTERVENTION_MINUTES = 5
SAMPLE_INTERVAL_SECONDS = 5
