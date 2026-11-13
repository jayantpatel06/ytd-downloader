"""
ytd/updater.py — Non-blocking GitHub release update checker.
"""

import json
import urllib.request
import webbrowser
from typing import Callable, Tuple

REPO_URL = "https://api.github.com/repos/jayantpatel06/ytd-downloader/releases/latest"


def parse_version(v_str: str) -> Tuple[int, ...]:
    """Parse a semantic version string like 'v1.0.2' into an integer tuple (1, 0, 2)."""
    clean = v_str.strip().lstrip("v")
    parts = []
    for item in clean.split("."):
        try:
            parts.append(int(item))
        except ValueError:
            break
    return tuple(parts)


def check_for_updates_async(current_version: str, on_update_available: Callable[[str, str], None]) -> None:
    """
    Check GitHub Releases for a newer version in a non-blocking background thread.
    Calls on_update_available(tag_name, html_url) if a newer version is found.
    """
    try:
        req = urllib.request.Request(
            REPO_URL,
            headers={
                "User-Agent": "ytd-app",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                latest_tag = data.get("tag_name", "")
                latest_ver = parse_version(latest_tag)
                current_ver = parse_version(current_version)

                if latest_ver > current_ver:
                    release_url = data.get("html_url", "https://github.com/jayantpatel06/ytd-downloader/releases")
                    on_update_available(latest_tag, release_url)
    except Exception:
        # Fails silently if offline or rate-limited
        pass


def open_release_page(url: str) -> None:
    """Open the release download page in the system default browser."""
    try:
        webbrowser.open(url)
    except Exception:
        pass
