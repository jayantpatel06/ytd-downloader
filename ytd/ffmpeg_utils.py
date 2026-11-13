"""
ytd/ffmpeg_utils.py — Detection and automated resolution for ffmpeg.
"""

import os
import shutil
import sys
import urllib.request
import zipfile


def get_appdata_ffmpeg_dir() -> str:
    """Return local application data directory for cached ffmpeg binary."""
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    target_dir = os.path.join(base, "ytd", "bin")
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def find_ffmpeg() -> str | None:
    """Search for ffmpeg across bundled, local, and system locations."""
    # 1. Bundled inside PyInstaller executable (_MEIPASS)
    if getattr(sys, "frozen", False):
        bundle_dir = getattr(sys, "_MEIPASS", "")
        if bundle_dir:
            bundled = os.path.join(bundle_dir, "ffmpeg.exe")
            if os.path.isfile(bundled):
                return bundled

        exe_dir = os.path.dirname(sys.executable)
        adjacent = os.path.join(exe_dir, "ffmpeg.exe")
        if os.path.isfile(adjacent):
            return adjacent

    # 2. Cached in AppData
    appdata_exe = os.path.join(get_appdata_ffmpeg_dir(), "ffmpeg.exe")
    if os.path.isfile(appdata_exe):
        return appdata_exe

    # 3. System PATH
    found = shutil.which("ffmpeg")
    if found:
        return found

    return None


def download_ffmpeg_if_missing(status_callback=None) -> str | None:
    """
    Download a standalone static ffmpeg binary for Windows if missing.
    Returns path to ffmpeg.exe or None on failure.
    """
    existing = find_ffmpeg()
    if existing:
        return existing

    if sys.platform != "win32":
        return None

    target_dir = get_appdata_ffmpeg_dir()
    ffmpeg_exe = os.path.join(target_dir, "ffmpeg.exe")
    zip_path = os.path.join(target_dir, "ffmpeg.zip")

    if status_callback:
        status_callback("Setting up media engine (first time only)...")

    # yt-dlp official static ffmpeg builds for Windows
    url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ytd-downloader"}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response, open(zip_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)

        with zipfile.ZipFile(zip_path, "r") as z:
            for member in z.namelist():
                # Extract only ffmpeg.exe, safely ignoring zip hierarchy
                if os.path.basename(member).lower() == "ffmpeg.exe":
                    with z.open(member) as source, open(ffmpeg_exe, "wb") as target:
                        shutil.copyfileobj(source, target)
                    break

        if os.path.isfile(ffmpeg_exe):
            return ffmpeg_exe
    except Exception as exc:
        print(f"[ytd] Automatic ffmpeg resolution skipped: {exc}", file=sys.stderr)
    finally:
        if os.path.exists(zip_path):
            try:
                os.remove(zip_path)
            except OSError:
                pass

    return None
