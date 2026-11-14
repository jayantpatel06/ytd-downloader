"""
ytd/ffmpeg_utils.py — Detection and automated resolution for ffmpeg.
"""

import os
import platform
import shutil
import sys
import tarfile
import urllib.request
import zipfile


def get_ffmpeg_bin_name() -> str:
    """Return platform executable name for ffmpeg."""
    return "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"


def get_appdata_ffmpeg_dir() -> str:
    """Return local application data directory for cached ffmpeg binary."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        target_dir = os.path.join(base, "ytd", "bin")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        target_dir = os.path.join(base, "ytd", "bin")
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def find_ffmpeg() -> str | None:
    """Search for ffmpeg across bundled, local, and system locations."""
    bin_name = get_ffmpeg_bin_name()

    # 1. Bundled inside PyInstaller executable (_MEIPASS)
    if getattr(sys, "frozen", False):
        bundle_dir = getattr(sys, "_MEIPASS", "")
        if bundle_dir:
            bundled = os.path.join(bundle_dir, bin_name)
            if os.path.isfile(bundled) and (sys.platform == "win32" or os.access(bundled, os.X_OK)):
                return bundled

        exe_dir = os.path.dirname(sys.executable)
        adjacent = os.path.join(exe_dir, bin_name)
        if os.path.isfile(adjacent) and (sys.platform == "win32" or os.access(adjacent, os.X_OK)):
            return adjacent

    # 2. Cached in AppData / ~/.local/share/ytd/bin
    cached_bin = os.path.join(get_appdata_ffmpeg_dir(), bin_name)
    if os.path.isfile(cached_bin) and (sys.platform == "win32" or os.access(cached_bin, os.X_OK)):
        return cached_bin

    # 3. System PATH
    found = shutil.which("ffmpeg")
    if found:
        return found

    return None


def download_ffmpeg_if_missing(status_callback=None) -> str | None:
    """
    Download a standalone static ffmpeg binary for Windows or Linux if missing.
    Returns path to ffmpeg executable or None on failure.
    """
    existing = find_ffmpeg()
    if existing:
        return existing

    target_dir = get_appdata_ffmpeg_dir()
    bin_name = get_ffmpeg_bin_name()
    target_bin = os.path.join(target_dir, bin_name)
    headers = {"User-Agent": "Mozilla/5.0 ytd-downloader"}

    # 1. Windows (x64)
    if sys.platform == "win32":
        url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        zip_path = os.path.join(target_dir, "ffmpeg.zip")

        if status_callback:
            status_callback("Setting up media engine (first time only)...")

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=45) as response, open(zip_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)

            with zipfile.ZipFile(zip_path, "r") as z:
                for member in z.namelist():
                    if os.path.basename(member).lower() == "ffmpeg.exe":
                        with z.open(member) as source, open(target_bin, "wb") as target:
                            shutil.copyfileobj(source, target)
                        break

            if os.path.isfile(target_bin):
                return target_bin
        except Exception as exc:
            print(f"[ytd] Automatic ffmpeg resolution skipped: {exc}", file=sys.stderr)
        finally:
            if os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except OSError:
                    pass

    # 2. Linux (x86_64 or aarch64)
    elif sys.platform.startswith("linux"):
        machine = platform.machine().lower()
        if machine in ("x86_64", "amd64"):
            url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
        elif machine in ("aarch64", "arm64"):
            url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl.tar.xz"
        else:
            return None

        archive_path = os.path.join(target_dir, "ffmpeg.tar.xz")

        if status_callback:
            status_callback("Setting up media engine (first time only)...")

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response, open(archive_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)

            with tarfile.open(archive_path, "r:xz") as tar:
                for member in tar.getmembers():
                    if os.path.basename(member.name) == "ffmpeg" and member.isfile():
                        extracted_f = tar.extractfile(member)
                        if extracted_f:
                            with open(target_bin, "wb") as target:
                                shutil.copyfileobj(extracted_f, target)
                            os.chmod(target_bin, 0o755)
                        break

            if os.path.isfile(target_bin):
                return target_bin
        except Exception as exc:
            print(f"[ytd] Automatic ffmpeg resolution skipped: {exc}", file=sys.stderr)
        finally:
            if os.path.exists(archive_path):
                try:
                    os.remove(archive_path)
                except OSError:
                    pass

    return None
