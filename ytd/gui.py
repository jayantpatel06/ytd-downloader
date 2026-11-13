"""
ytd/gui.py — Desktop GUI for YouTube Downloader with in-app self-updater and cancellation.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from yt_dlp import YoutubeDL
from ytd import __version__
from ytd.ffmpeg_utils import find_ffmpeg, download_ffmpeg_if_missing
from ytd.updater import (
    apply_update_and_restart,
    check_for_updates_async,
    download_update_stream,
)


class DownloadCancelledError(Exception):
    """Raised when the user cancels an in-progress download."""
    pass


def run_gui():
    root = tk.Tk()
    root.title(f"YouTube Downloader (v{__version__})")
    root.geometry("480x350")
    root.resizable(False, False)

    download_dir = {"path": ""}
    is_downloading = {"active": False}
    cancel_requested = {"active": False}

    # Set window icon
    try:
        from ytd.cli import _get_icon_path
        ico = _get_icon_path()
        if ico and os.path.exists(ico):
            root.iconbitmap(ico)
    except Exception:
        pass

    # Thread-safe UI update helpers
    def set_status(text: str):
        root.after(0, lambda: status_label.config(text=text))

    def set_progress(value: float):
        root.after(0, lambda: progress_bar.configure(value=value))

    def set_action_btn(text: str, state: str = "normal"):
        root.after(0, lambda: action_btn.config(text=text, state=state))

    def show_error(title: str, message: str):
        root.after(0, lambda: messagebox.showerror(title, message))

    # In-app self-update banner
    def show_update_banner(tag_name: str, download_url: str):
        def _build():
            banner = tk.Frame(root, bg="#0f172a", pady=5, padx=12)
            banner.pack(side="bottom", fill="x")

            is_frozen = getattr(sys, "frozen", False)
            text_var = tk.StringVar(value=f"Update available ({tag_name})")
            lbl = tk.Label(
                banner,
                textvariable=text_var,
                fg="#f1f5f9",
                bg="#0f172a",
                font=("Arial", 9),
            )
            lbl.pack(side="left")

            ready_temp_path = {"path": ""}

            def on_update_click():
                if ready_temp_path["path"]:
                    apply_update_and_restart(ready_temp_path["path"])
                    return

                if not is_frozen:
                    import webbrowser
                    webbrowser.open("https://github.com/jayantpatel06/ytd-downloader/releases")
                    return

                update_btn.config(state="disabled")
                text_var.set("Downloading update... 0%")

                def on_progress(pct: float):
                    root.after(0, lambda: text_var.set(f"Downloading update... {pct:.0f}%"))

                def on_complete(temp_path: str):
                    ready_temp_path["path"] = temp_path
                    root.after(0, lambda: text_var.set(f"Version {tag_name} ready."))
                    root.after(0, lambda: update_btn.config(text="Restart Now", state="normal"))

                def on_err(err_msg: str):
                    root.after(0, lambda: text_var.set("Update failed."))
                    root.after(0, lambda: update_btn.config(text="Retry", state="normal"))

                threading.Thread(
                    target=download_update_stream,
                    args=(download_url, on_progress, on_complete, on_err),
                    daemon=True,
                ).start()

            btn_label = "Update" if is_frozen else "View"
            update_btn = tk.Button(
                banner,
                text=btn_label,
                command=on_update_click,
                font=("Arial", 8, "bold"),
                padx=8,
                pady=1,
            )
            update_btn.pack(side="right")

        root.after(0, _build)

    def on_action_click():
        if is_downloading["active"]:
            cancel_requested["active"] = True
            set_status("Cancelling download...")
            set_action_btn("Cancelling...", state="disabled")
        else:
            url = url_entry.get().strip()
            if not url:
                messagebox.showerror("Error", "Please enter a valid video or playlist link.")
                return

            if not (url.startswith("http://") or url.startswith("https://")):
                messagebox.showerror("Error", "URL must start with http:// or https://")
                return

            is_downloading["active"] = True
            cancel_requested["active"] = False
            t = threading.Thread(target=perform_download, args=(url,), daemon=True)
            t.start()

    def perform_download(url: str):
        quality = quality_var.get()
        out_dir = download_dir["path"] or "."
        out_template = os.path.join(out_dir, "%(title)s.%(ext)s")

        set_progress(0)
        set_status("Starting download...")
        set_action_btn("Cancel")

        def progress_hook(d):
            if cancel_requested["active"]:
                raise DownloadCancelledError()

            if d.get("status") == "downloading":
                raw = str(d.get("_percent_str", "0%")).replace("%", "").strip()
                try:
                    pct = float(raw)
                except ValueError:
                    pct = 0.0
                set_progress(pct)
                speed = d.get("_speed_str", "")
                eta = d.get("_eta_str", "")
                set_status(f"Downloading... {pct:.1f}%  {speed}  ETA {eta}")
            elif d.get("status") == "finished":
                set_status("Merging video and audio...")

        # Resolve or fetch ffmpeg
        ffmpeg_bin = find_ffmpeg()
        if not ffmpeg_bin:
            set_status("Setting up media engine (first time only)...")
            ffmpeg_bin = download_ffmpeg_if_missing()

        fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
        ydl_opts = {
            "format": fmt,
            "merge_output_format": "mp4",
            "progress_hooks": [progress_hook],
            "outtmpl": out_template,
            "noplaylist": not playlist_var.get(),
            "quiet": True,
            "no_warnings": True,
        }
        if ffmpeg_bin:
            ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_bin)

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            set_progress(100)
            set_status("Download completed.")
        except DownloadCancelledError:
            set_progress(0)
            set_status("Download cancelled.")
        except Exception as exc:
            if cancel_requested["active"]:
                set_progress(0)
                set_status("Download cancelled.")
            else:
                show_error("Download Failed", str(exc))
                set_status("Error occurred.")
        finally:
            is_downloading["active"] = False
            cancel_requested["active"] = False
            set_action_btn("Download")

    def choose_directory():
        path = filedialog.askdirectory(title="Choose download folder")
        if path:
            download_dir["path"] = path
            dir_label.config(text=path)

    def on_window_close():
        if is_downloading["active"]:
            cancel_requested["active"] = True
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_window_close)

    # UI Layout
    tk.Label(root, text="YouTube Downloader", font=("Arial", 16, "bold")).pack(pady=(10, 2))

    tk.Label(root, text="Video or Playlist URL:").pack()
    url_entry = tk.Entry(root, width=58)
    url_entry.pack(pady=4)

    row_q = tk.Frame(root)
    row_q.pack(pady=4)
    tk.Label(row_q, text="Quality:").pack(side="left")
    quality_var = tk.StringVar()
    quality_dd = ttk.Combobox(
        row_q, textvariable=quality_var, state="readonly",
        values=["360", "480", "720", "1080", "1440", "2160"], width=6,
    )
    quality_dd.current(3)
    quality_dd.pack(side="left", padx=6)

    playlist_var = tk.BooleanVar(value=False)
    tk.Checkbutton(row_q, text="Download playlist", variable=playlist_var).pack(side="left", padx=10)

    row_dir = tk.Frame(root)
    row_dir.pack(pady=2)
    tk.Button(row_dir, text="Browse...", command=choose_directory).pack(side="left")
    dir_label = tk.Label(row_dir, text="(current folder by default)", fg="grey")
    dir_label.pack(side="left", padx=8)

    action_btn = tk.Button(
        root, text="Download", command=on_action_click,
        width=22, font=("Arial", 11, "bold")
    )
    action_btn.pack(pady=8)

    progress_bar = ttk.Progressbar(root, length=400, maximum=100)
    progress_bar.pack(pady=4)
    status_label = tk.Label(root, text="Ready", font=("Arial", 10))
    status_label.pack(pady=(0, 4))

    # Background update check (non-blocking)
    threading.Thread(
        target=check_for_updates_async,
        args=(__version__, show_update_banner),
        daemon=True,
    ).start()

    root.mainloop()


if __name__ == "__main__":
    run_gui()
