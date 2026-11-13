"""
ytd/gui.py — Tkinter GUI for YouTube Downloader
"""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from yt_dlp import YoutubeDL
from ytd.ffmpeg_utils import find_ffmpeg, download_ffmpeg_if_missing
import os


def run_gui():
    download_dir = {"path": ""}

    def start_download_thread():
        t = threading.Thread(target=start_download, daemon=True)
        t.start()

    def start_download():
        url = url_entry.get().strip()
        quality = quality_var.get()
        out_dir = download_dir["path"] or "."

        if not url:
            messagebox.showerror("Error", "Enter a YouTube / supported-site link first.")
            return

        progress_bar["value"] = 0
        status_label.config(text="Starting download…")
        download_btn.config(state="disabled")
        root.update_idletasks()

        def progress_hook(d):
            if d["status"] == "downloading":
                raw = d.get("_percent_str", "0%").replace("%", "").strip()
                try:
                    pct = float(raw)
                except ValueError:
                    pct = 0.0
                progress_bar["value"] = pct
                speed = d.get("_speed_str", "")
                eta = d.get("_eta_str", "")
                status_label.config(text=f"Downloading… {pct:.1f}%  {speed}  ETA {eta}")
                root.update_idletasks()
            elif d["status"] == "finished":
                status_label.config(text="Merging video + audio…")
                root.update_idletasks()

        # Ensure ffmpeg is resolved
        ffmpeg_bin = find_ffmpeg()
        if not ffmpeg_bin:
            status_label.config(text="Setting up media engine (first time only)...")
            root.update_idletasks()
            ffmpeg_bin = download_ffmpeg_if_missing()

        fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
        ydl_opts = {
            "format": fmt,
            "merge_output_format": "mp4",
            "progress_hooks": [progress_hook],
            "outtmpl": f"{out_dir}/%(title)s.%(ext)s",
            "noplaylist": not playlist_var.get(),
        }
        if ffmpeg_bin:
            ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_bin)

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            progress_bar["value"] = 100
            status_label.config(text="✅ Download completed!")
        except Exception as exc:
            messagebox.showerror("Download failed", str(exc))
            status_label.config(text="❌ Error occurred.")
        finally:
            download_btn.config(state="normal")

    def choose_directory():
        path = filedialog.askdirectory(title="Choose download folder")
        if path:
            download_dir["path"] = path
            dir_label.config(text=f"📁 {path}")

    root = tk.Tk()
    root.title("YouTube Downloader  v1.0")
    root.geometry("480x320")
    root.resizable(False, False)

    tk.Label(root, text="YouTube Downloader", font=("Arial", 16, "bold")).pack(pady=(12, 2))

    tk.Label(root, text="Video / Playlist URL:").pack()
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
    tk.Button(row_dir, text="📁 Choose folder", command=choose_directory).pack(side="left")
    dir_label = tk.Label(row_dir, text="(saves next to exe by default)", fg="grey")
    dir_label.pack(side="left", padx=8)

    download_btn = tk.Button(root, text="⬇  Download", command=start_download_thread,
                             width=22, font=("Arial", 11, "bold"))
    download_btn.pack(pady=10)

    progress_bar = ttk.Progressbar(root, length=400, maximum=100)
    progress_bar.pack(pady=4)
    status_label = tk.Label(root, text="Waiting…", font=("Arial", 10))
    status_label.pack()

    root.mainloop()


if __name__ == "__main__":
    run_gui()

