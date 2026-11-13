"""
ytd/cli.py — Entry point for the ytd application (GUI and CLI).
"""

import argparse
import os
import sys


def _attach_console():
    """Attach to parent console on Windows when running from terminal."""
    if sys.platform == "win32":
        try:
            import ctypes
            if ctypes.windll.kernel32.AttachConsole(-1):
                sys.stdout = open("CONOUT$", "w", encoding="utf-8", errors="replace")
                sys.stderr = open("CONOUT$", "w", encoding="utf-8", errors="replace")
        except Exception:
            pass


def _get_icon_path() -> str:
    """Return path to the icon across frozen exe, installed, or source modes."""
    candidates = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", "")
        if meipass:
            candidates.append(os.path.join(meipass, "assets", "ytd_icon.ico"))
            candidates.append(os.path.join(meipass, "ytd_icon.ico"))
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(os.path.join(exe_dir, "ytd_icon.ico"))
        candidates.append(os.path.join(exe_dir, "assets", "ytd_icon.ico"))
    else:
        candidates.append(os.path.join(os.path.dirname(__file__), "..", "assets", "ytd_icon.ico"))

    local_appdata = os.environ.get("LOCALAPPDATA", "")
    if local_appdata:
        candidates.append(os.path.join(local_appdata, "Programs", "YTD", "ytd_icon.ico"))

    for c in candidates:
        if c and os.path.exists(c):
            return os.path.abspath(c)
    return ""


def main():
    parser = argparse.ArgumentParser(
        prog="ytd",
        description="YouTube and multi-site video downloader powered by yt-dlp.",
    )
    parser.add_argument("url", nargs="?", help="Video or playlist URL to download")
    parser.add_argument("--gui", action="store_true", help="Launch the GUI")
    parser.add_argument(
        "-q", "--quality", default="1080",
        choices=["360", "480", "720", "1080", "1440", "2160"],
        help="Maximum video height in pixels (default: 1080)",
    )
    parser.add_argument("-o", "--output", default=".", help="Output directory (default: current directory)")
    parser.add_argument("--playlist", action="store_true", help="Download complete playlist")
    parser.add_argument("-a", "--audio-only", action="store_true", help="Download audio only as MP3")
    parser.add_argument("--version", action="version", version="ytd 1.0.0")

    args = parser.parse_args()

    # Create desktop shortcut on first run
    try:
        from ytd.shortcut import ensure_shortcut
        ensure_shortcut(icon_path=_get_icon_path())
    except Exception:
        pass

    # Launch GUI when no URL is provided or --gui is requested
    if args.gui or not args.url:
        from ytd.gui import run_gui
        run_gui()
        return

    # CLI mode: attach console output for Windows GUI subsystem
    _attach_console()

    url = args.url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        print("[ytd] Error: Invalid URL. Must start with http:// or https://", file=sys.stderr)
        sys.exit(1)

    from yt_dlp import YoutubeDL
    from ytd.ffmpeg_utils import find_ffmpeg, download_ffmpeg_if_missing

    ffmpeg_bin = find_ffmpeg() or download_ffmpeg_if_missing()

    if args.audio_only:
        fmt = "bestaudio/best"
        postprocessors = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    else:
        fmt = f"bestvideo[height<={args.quality}]+bestaudio/best[height<={args.quality}]"
        postprocessors = []

    out_template = os.path.join(args.output, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": fmt,
        "merge_output_format": "mp4" if not args.audio_only else None,
        "postprocessors": postprocessors,
        "outtmpl": out_template,
        "noplaylist": not args.playlist,
    }
    if ffmpeg_bin:
        ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_bin)

    print(f"[ytd] Downloading: {url}")
    print(f"[ytd] Quality: {'audio-only (MP3)' if args.audio_only else args.quality + 'p'} -> {args.output}")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("[ytd] Done.")
    except Exception as exc:
        print(f"[ytd] Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
