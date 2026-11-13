"""
ytd/cli.py — Entry-point for the ytd command.

Usage:
    ytd                          # launches the GUI
    ytd --gui                    # explicitly launch GUI
    ytd <URL>                    # download best quality to current dir
    ytd <URL> -q 720             # download at <=720p
    ytd <URL> -o ~/Videos        # save to custom folder
    ytd <URL> --playlist         # download entire playlist
    ytd <URL> -a                 # audio-only (MP3)
"""

import argparse
import os
import sys


def _get_icon_path() -> str:
    """Return path to the bundled icon (works in PyInstaller and from source)."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # PyInstaller temp dir
    else:
        base = os.path.join(os.path.dirname(__file__), "..", "assets")
    ico = os.path.join(base, "ytd_icon.ico")
    return ico if os.path.exists(ico) else ""


def main():
    parser = argparse.ArgumentParser(
        prog="ytd",
        description="YouTube / multi-site video downloader (yt-dlp powered)",
    )
    parser.add_argument("url", nargs="?", help="Video or playlist URL to download")
    parser.add_argument("--gui", action="store_true", help="Launch the GUI (default when no URL given)")
    parser.add_argument("-q", "--quality", default="1080",
                        choices=["360", "480", "720", "1080", "1440", "2160"],
                        help="Max video height in pixels (default: 1080)")
    parser.add_argument("-o", "--output", default=".",
                        help="Output directory (default: current dir)")
    parser.add_argument("--playlist", action="store_true",
                        help="Download full playlist instead of single video")
    parser.add_argument("-a", "--audio-only", action="store_true",
                        help="Download audio only as MP3")
    parser.add_argument("--version", action="version", version="ytd 1.0.0")

    args = parser.parse_args()

    # ── Create desktop shortcut silently on first run ─────────────────────────
    try:
        from ytd.shortcut import ensure_shortcut
        ensure_shortcut(icon_path=_get_icon_path())
    except Exception:
        pass  # Never break the app over a shortcut failure

    # ── Launch GUI when no URL given or --gui flag ────────────────────────────
    if args.gui or not args.url:
        from ytd.gui import run_gui
        run_gui()
        return

    # ── CLI download ──────────────────────────────────────────────────────────
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

    ydl_opts = {
        "format": fmt,
        "merge_output_format": "mp4" if not args.audio_only else None,
        "postprocessors": postprocessors,
        "outtmpl": f"{args.output}/%(title)s.%(ext)s",
        "noplaylist": not args.playlist,
    }
    if ffmpeg_bin:
        ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_bin)

    print(f"[ytd] Downloading: {args.url}")
    print(f"[ytd] Quality: {'audio-only' if args.audio_only else args.quality + 'p'}  →  {args.output}")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([args.url])
        print("[ytd] ✅ Done!")
    except Exception as exc:
        print(f"[ytd] ❌ Failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

