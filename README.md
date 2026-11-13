# YouTube Downloader (ytd)

> A simple, cross-platform YouTube / multi-site video downloader powered by **yt-dlp**.
> Ships with a **GUI** (tkinter) and a full **CLI** — zero configuration needed.

---

## ✨ Features

- 🖥️ Clean GUI with quality picker, folder chooser, progress bar
- 💻 CLI for scripting / headless use
- 🎵 Audio-only (MP3) download
- 📋 Playlist support
- Supports every site yt-dlp supports (YouTube, Twitter/X, Vimeo, …)

---

## 📦 Installation

### Option 1 — pip (recommended, one line)

```bash
pip install ytd-downloader
```

Then launch the GUI:

```bash
ytd          # launches GUI automatically
```

Or use the CLI:

```bash
ytd "https://youtu.be/dQw4w9WgXcQ"
```

---

### Option 2 — Download the standalone `.exe` (Windows, no Python needed)

1. Go to [**Releases**](https://github.com/jayantpatel06/ytd-downloader/releases)
2. Download `ytd.exe` from the latest release
3. Double-click to open the GUI **or** run from your terminal:

```cmd
ytd.exe "https://youtu.be/dQw4w9WgXcQ" -q 1080
```

> **Tip:** Add the folder containing `ytd.exe` to your `PATH` so you can run `ytd` from anywhere.

---

### Option 3 — Run from source

```bash
git clone https://github.com/jayantpatel06/ytd-downloader.git
cd ytd-downloader
pip install -r requirements.txt
python -m ytd.cli          # GUI
python -m ytd.cli "URL"    # CLI download
```

---

## 🖥️ GUI Usage

Just run `ytd` (or double-click the `.exe`).

| Field | Description |
|-------|-------------|
| **URL** | Paste any YouTube or supported-site link |
| **Quality** | 360 / 480 / 720 / 1080 / 1440 / 2160p |
| **Download playlist** | Check to grab the full playlist |
| **Choose folder** | Pick where files are saved (default: current dir) |

---

## 💻 CLI Usage

```
ytd [URL] [options]

Options:
  -q, --quality   360|480|720|1080|1440|2160  (default: 1080)
  -o, --output    Output directory            (default: .)
  --playlist      Download entire playlist
  -a, --audio-only  Audio only as MP3
  --gui           Force GUI mode
  --version       Show version and exit
  -h, --help      Show help
```

### Examples

```bash
# GUI
ytd

# Download at best quality ≤1080p to current directory
ytd "https://youtu.be/dQw4w9WgXcQ"

# Download at 720p to ~/Videos
ytd "https://youtu.be/dQw4w9WgXcQ" -q 720 -o ~/Videos

# Audio only (MP3)
ytd "https://youtu.be/dQw4w9WgXcQ" -a

# Download a whole playlist
ytd "https://youtube.com/playlist?list=PLXXX" --playlist -o ~/Playlists
```

---

## 🔧 Requirements

| Requirement | Notes |
|-------------|-------|
| Python ≥ 3.9 | Only for pip / source install; not needed for `.exe` |
| **ffmpeg** | Required for merging video + audio streams |
| yt-dlp | Installed automatically with pip |

### Installing ffmpeg

| Platform | Command |
|----------|---------|
| **Windows** | `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html) |
| **macOS** | `brew install ffmpeg` |
| **Linux** | `sudo apt install ffmpeg` or `sudo dnf install ffmpeg` |

---

## 🏗️ Building the `.exe` yourself

```bash
pip install pyinstaller
python build_exe.py
# → dist/ytd.exe
```

---

## 🤝 Contributing

Pull requests are welcome! Please open an issue first to discuss major changes.

---

## 📄 License

[MIT](LICENSE)

