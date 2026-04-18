from typing import List
import psutil
import sys

FOCUS_KEYWORDS = [
    "code",
    "editor",
    "word",
    "excel",
    "research",
    "project",
    "email",
    "meeting",
    "presentation",
]

DISTRACTION_KEYWORDS = [
    "youtube",
    "facebook",
    "twitter",
    "instagram",
    "tiktok",
    "netflix",
    "discord",
    "reddit",
]


def scan_active_window() -> str:
    if sys.platform.startswith("win"):
        try:
            from pywinauto import Desktop
            active = Desktop(backend="uia").get_active()
            return active.window_text() or ""
        except Exception:
            return ""
    return ""


def categorize_window(title: str) -> str:
    lowered = title.lower()
    if any(token in lowered for token in DISTRACTION_KEYWORDS):
        return "distractor"
    if any(token in lowered for token in FOCUS_KEYWORDS):
        return "focus"
    return "neutral"


def list_process_names(limit: int = 20) -> List[str]:
    names = []
    for proc in psutil.process_iter(attrs=["name"]):
        try:
            names.append(proc.info["name"] or "")
        except psutil.NoSuchProcess:
            continue
        if len(names) >= limit:
            break
    return names
