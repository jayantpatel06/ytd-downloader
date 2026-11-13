"""
ytd/ffmpeg_utils.py — Automatic detection and resolution for ffmpeg.

Ensures that even if the end user has neither Python nor ffmpeg installed:
1. Checks if ffmpeg.exe is bundled inside the PyInstaller executable (_MEIPASS).
2. Checks if ffmpeg.exe is sitting in the same folder as the executable.
3. Checks if ffmpeg is in user's AppData/Local/ytd/bin/.
4. Checks system PATH.
5. If completely missing, provides an automatic background downloader for ffmpeg.
"""

import os
import shutil
import sys
import urllib.request
import zipfile


def get_appdata_ffmpeg_dir() -> str:
    """Folder in user's AppData where standalone ffmpeg can live."""
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    target_dir = os.path.join(base, "ytd", "bin")
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def find_ffmpeg() -> str | None:
    """Find path to ffmpeg.exe across all possible locations."""
    # 1. Bundled inside PyInstaller single-file exe
    if getattr(sys, "frozen", False):
        bundle_dir = getattr(sys, "_MEIPASS", "")
        if bundle_dir:
            bundled = os.path.join(bundle_dir, "ffmpeg.exe")
            if os.path.exists(bundled):
                return bundled

        # Next to the .exe itself
        exe_dir = os.path.dirname(sys.executable)
        adjacent = os.path.join(exe_dir, "ffmpeg.exe")
        if os.path.exists(adjacent):
            return adjacent

    # 2. LocalAppData cache
    appdata_exe = os.path.join(get_appdata_ffmpeg_dir(), "ffmpeg.exe")
    if os.path.exists(appdata_exe):
        return appdata_exe

    # 3. System PATH
    found_in_path = shutil.which("ffmpeg")
    if found_in_path:
        return found_in_path

    return None


def download_ffmpeg_if_missing(status_callback=None) -> str | None:
    """
    Downloads a lightweight static ffmpeg build for Windows if missing.
    Returns path to ffmpeg.exe, or None on failure.
    """
    existing = find_ffmpeg()
    if existing:
        return existing

    if sys.platform != "win32":
        return None  # On Linux/macOS users usually have package managers

    target_dir = get_appdata_ffmpeg_dir()
    ffmpeg_exe = os.path.join(target_dir, "ffmpeg.exe")

    if status_callback:
        status_callback("Setting up media engine (one-time setup)...")

    # URL to yt-dlp's curated, reliable Windows static ffmpeg build
    url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = os.path.join(target_dir, "ffmpeg.zip")

    try:
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as z:
            for member in z.namelist():
                if member.endswith("ffmpeg.exe"):
                    with z.open(member) as source, open(ffmpeg_exe, "wb") as target:
                        shutil.copyfileobj(source, target)
                    break
        if os.path.exists(zip_path):
            os.remove(zip_path)

        if os.path.exists(ffmpeg_exe):
            return ffmpeg_exe
    except Exception as e:
        print(f"[ytd] Automatic ffmpeg setup skipped: {e}", file=sys.stderr)

    return None
