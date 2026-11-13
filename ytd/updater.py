"""
ytd/updater.py — In-app self-updater: downloads new binary and replaces in-place.
"""

import json
import os
import shutil
import subprocess
import sys
import threading
import urllib.request
from typing import Callable, Tuple

REPO_API_URL = "https://api.github.com/repos/jayantpatel06/ytd-downloader/releases/latest"
DEFAULT_DOWNLOAD_URL = "https://github.com/jayantpatel06/ytd-downloader/releases/latest/download/ytd.exe"


def parse_version(v_str: str) -> Tuple[int, ...]:
    """Parse semantic version string like 'v1.0.2' into an integer tuple (1, 0, 2)."""
    clean = v_str.strip().lstrip("v")
    parts = []
    for item in clean.split("."):
        try:
            parts.append(int(item))
        except ValueError:
            break
    return tuple(parts)


def check_for_updates_async(
    current_version: str,
    on_update_found: Callable[[str, str], None],
) -> None:
    """
    Check GitHub Releases for a newer version in a non-blocking background thread.
    Calls on_update_found(tag_name, download_url) if a newer version is available.
    """
    try:
        req = urllib.request.Request(
            REPO_API_URL,
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
                    download_url = DEFAULT_DOWNLOAD_URL
                    for asset in data.get("assets", []):
                        if asset.get("name") == "ytd.exe":
                            download_url = asset.get("browser_download_url")
                            break
                    on_update_found(latest_tag, download_url)
    except Exception:
        # Fails silently if offline or rate-limited
        pass


def download_update_stream(
    download_url: str,
    progress_callback: Callable[[float], None],
    on_complete: Callable[[str], None],
    on_error: Callable[[str], None],
) -> None:
    """
    Download the new ytd.exe binary to a temporary file with live progress.
    Validates PE header to ensure safe binary replacement.
    """
    temp_dir = os.environ.get("TEMP") or os.path.dirname(sys.executable)
    target_temp_exe = os.path.join(temp_dir, "ytd_update.exe")

    try:
        req = urllib.request.Request(
            download_url,
            headers={"User-Agent": "ytd-updater"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp, open(target_temp_exe, "wb") as out:
            total_size = int(resp.headers.get("content-length", 0))
            downloaded = 0
            chunk_size = 65536

            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                out.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    pct = (downloaded / total_size) * 100.0
                    progress_callback(min(pct, 99.9))

        # Security check: verify downloaded file is a valid Windows executable (PE header: 'MZ')
        with open(target_temp_exe, "rb") as f:
            header = f.read(2)
            if header != b"MZ":
                os.remove(target_temp_exe)
                on_error("Downloaded file failed executable validation.")
                return

        progress_callback(100.0)
        on_complete(target_temp_exe)

    except Exception as exc:
        if os.path.exists(target_temp_exe):
            try:
                os.remove(target_temp_exe)
            except OSError:
                pass
        on_error(str(exc))


def apply_update_and_restart(temp_exe_path: str) -> None:
    """
    Atomically replace running executable and restart.
    Uses detached shell command to wait for process exit, overwrite, and relaunch.
    """
    current_exe = os.path.abspath(sys.executable)

    if not getattr(sys, "frozen", False):
        # In development/source mode, do not overwrite Python interpreter!
        return

    if sys.platform == "win32":
        cmd = (
            f'timeout /t 1 /nobreak >nul & '
            f'move /y "{temp_exe_path}" "{current_exe}" >nul & '
            f'start "" "{current_exe}"'
        )
        # DETACHED_PROCESS = 0x00000008, CREATE_NO_WINDOW = 0x08000000
        flags = 0x00000008 | 0x08000000
        subprocess.Popen(
            ["cmd.exe", "/c", cmd],
            creationflags=flags,
            close_fds=True,
        )
        sys.exit(0)
