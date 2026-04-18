import os
import sys
from pathlib import Path
from typing import List
from .config import BLOCKED_SITES

if sys.platform.startswith("win"):
    HOSTS_FILE = Path(r"C:\Windows\System32\drivers\etc\hosts")
elif sys.platform.startswith("darwin"):
    HOSTS_FILE = Path("/etc/hosts")
else:
    HOSTS_FILE = Path("/etc/hosts")

BLOCK_MARKER_START = "# focusflow-block-start"
BLOCK_MARKER_END = "# focusflow-block-end"


def _read_hosts() -> str:
    try:
        return HOSTS_FILE.read_text(encoding="utf-8")
    except PermissionError:
        return ""


def _write_hosts(content: str):
    HOSTS_FILE.write_text(content, encoding="utf-8")


def block_sites(extra_urls: List[str] = None):
    urls = list(BLOCKED_SITES)
    if extra_urls:
        urls.extend(extra_urls)
    content = _read_hosts()
    if BLOCK_MARKER_START in content and BLOCK_MARKER_END in content:
        return
    block_entries = "\n".join(f"127.0.0.1 {url}" for url in urls)
    new_content = f"{content}\n{BLOCK_MARKER_START}\n{block_entries}\n{BLOCK_MARKER_END}\n"
    _write_hosts(new_content)


def unblock_sites():
    content = _read_hosts()
    if not content:
        return
    start = content.find(BLOCK_MARKER_START)
    end = content.find(BLOCK_MARKER_END)
    if start == -1 or end == -1:
        return
    cleaned = content[:start] + content[end + len(BLOCK_MARKER_END):]
    _write_hosts(cleaned)
