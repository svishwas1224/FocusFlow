import sys
import time
import threading
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Deque, Dict, List, Optional

import psutil

try:
    from pynput import keyboard, mouse
except ImportError:
    keyboard = None  # type: ignore
    mouse = None  # type: ignore

try:
    from plyer import notification
except ImportError:
    notification = None  # type: ignore

from .analytics import calculate_focus_score, event_density_to_rate
from .config import (
    BLOCKED_SITES,
    DISTRACTOR_KEYWORDS,
    FORBIDDEN_APPS,
    FOCUS_KEYWORDS,
    INTERVENTION_MINUTES,
    INTERVENTION_THRESHOLD_SCORE,
    SAMPLE_INTERVAL_SECONDS,
)

if sys.platform.startswith("win"):
    HOSTS_FILE = Path(r"C:\Windows\System32\drivers\etc\hosts")
elif sys.platform.startswith("darwin"):
    HOSTS_FILE = Path("/etc/hosts")
else:
    HOSTS_FILE = Path("/etc/hosts")

BLOCK_MARKER_START = "# focusflow-block-start"
BLOCK_MARKER_END = "# focusflow-block-end"


@dataclass
class FocusState:
    title: str = ""
    category: str = "neutral"
    focus_score: int = 0
    activity_rate: float = 0.0
    forbidden: bool = False
    intervention_required: bool = False
    last_update: float = field(default_factory=time.time)


class ActivityMonitor:
    def __init__(self):
        self._event_timestamps: Deque[float] = deque(maxlen=300)
        self._lock = threading.Lock()
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._keyboard_listener = None
        self._mouse_listener = None
        self.state = FocusState()
        self._low_score_start: Optional[float] = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._start_input_listeners()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop(self) -> None:
        self._running = False
        self._stop_input_listeners()
        self.unblock_sites()

    def record_event(self) -> None:
        with self._lock:
            self._event_timestamps.append(time.time())

    def get_activity_rate(self) -> float:
        cutoff = time.time() - 60
        with self._lock:
            while self._event_timestamps and self._event_timestamps[0] < cutoff:
                self._event_timestamps.popleft()
            return float(len(self._event_timestamps)) / 60.0

    def _on_key(self, _):
        self.record_event()

    def _on_move(self, _, __):
        self.record_event()

    def _start_input_listeners(self) -> None:
        if keyboard and mouse:
            try:
                self._keyboard_listener = keyboard.Listener(on_press=self._on_key)
                self._mouse_listener = mouse.Listener(on_move=self._on_move, on_click=lambda *args: self.record_event())
                self._keyboard_listener.start()
                self._mouse_listener.start()
            except Exception:
                self._keyboard_listener = None
                self._mouse_listener = None

    def _stop_input_listeners(self) -> None:
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None

    def _monitor_loop(self) -> None:
        while self._running:
            title = self.scan_active_window()
            category = self.categorize_window(title)
            activity_rate = self.get_activity_rate()
            forbidden = self.is_forbidden(title)
            focus_score = calculate_focus_score(category, activity_rate, forbidden)
            intervention = self._should_intervene(focus_score)
            self.state = FocusState(
                title=title,
                category=category,
                focus_score=focus_score,
                activity_rate=activity_rate,
                forbidden=forbidden,
                intervention_required=intervention,
                last_update=time.time(),
            )
            if forbidden:
                self._trigger_intervention(title)
            time.sleep(SAMPLE_INTERVAL_SECONDS)

    @staticmethod
    def scan_active_window() -> str:
        if sys.platform.startswith("win"):
            try:
                import ctypes
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                return buf.value if buf.value else ""
            except Exception:
                return ""
        return ""

    @staticmethod
    def categorize_window(title: str) -> str:
        lowered = title.lower()
        if any(token in lowered for token in DISTRACTOR_KEYWORDS):
            return "distractor"
        if any(token in lowered for token in FOCUS_KEYWORDS):
            return "focus"
        return "neutral"

    @staticmethod
    def is_forbidden(title: str) -> bool:
        lowered = title.lower()
        return any(forbidden in lowered for forbidden in FORBIDDEN_APPS)

    def _should_intervene(self, score: int) -> bool:
        if score < INTERVENTION_THRESHOLD_SCORE:
            if self._low_score_start is None:
                self._low_score_start = time.time()
            return time.time() - self._low_score_start > INTERVENTION_MINUTES * 60
        self._low_score_start = None
        return False

    def _trigger_intervention(self, title: str) -> None:
        self.minimize_active_window()
        self.notify_user(
            "FocusFlow AI detected a blocked window and minimized it. Stay on task."
        )

    def minimize_active_window(self) -> None:
        if not sys.platform.startswith("win"):
            return
        try:
            from pywinauto import Desktop

            active = Desktop(backend="uia").get_active()
            if active:
                active.minimize()
        except Exception:
            pass

    @staticmethod
    def notify_user(message: str) -> None:
        if notification is None:
            return
        try:
            notification.notify(title="FocusFlow AI", message=message, timeout=5)
        except Exception:
            pass

    def block_sites(self, extra_urls: Optional[List[str]] = None) -> bool:
        urls = list(BLOCKED_SITES)
        if extra_urls:
            urls.extend(extra_urls)
        content = self._read_hosts()
        if BLOCK_MARKER_START in content and BLOCK_MARKER_END in content:
            return True
        block_entries = "\n".join(f"127.0.0.1 {url}" for url in urls)
        new_content = f"{content}\n{BLOCK_MARKER_START}\n{block_entries}\n{BLOCK_MARKER_END}\n"
        return self._write_hosts_safe(new_content)

    def unblock_sites(self) -> bool:
        content = self._read_hosts()
        if not content:
            return True
        start = content.find(BLOCK_MARKER_START)
        end = content.find(BLOCK_MARKER_END)
        if start == -1 or end == -1:
            return True
        cleaned = content[:start] + content[end + len(BLOCK_MARKER_END):]
        return self._write_hosts_safe(cleaned)

    @staticmethod
    def _read_hosts() -> str:
        try:
            return HOSTS_FILE.read_text(encoding="utf-8")
        except Exception:
            return ""

    @staticmethod
    def _write_hosts_safe(content: str) -> bool:
        try:
            HOSTS_FILE.write_text(content, encoding="utf-8")
            return True
        except PermissionError:
            return False
        except Exception:
            return False

    @staticmethod
    def list_process_names(limit: int = 20) -> List[str]:
        names: List[str] = []
        for proc in psutil.process_iter(attrs=["name"]):
            try:
                names.append(proc.info["name"] or "")
            except psutil.NoSuchProcess:
                continue
            if len(names) >= limit:
                break
        return names


monitor = ActivityMonitor()
