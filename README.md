# YouTube Downloader (ytd)

<p align="center">
  <img src="assets/ytd_icon.png" width="96" height="96" alt="YouTube Downloader Logo">
  <br>
  <b>A fast, minimal video and audio downloader powered by yt-dlp.</b>
  <br>
  <span>Includes both a desktop GUI and a command-line interface. Automatic FFmpeg setup included.</span>
  <br><br>
  <a href="https://github.com/jayantpatel06/ytd-downloader/releases/latest/download/ytd-setup.exe">
    <img src="https://img.shields.io/badge/Download-Windows_Installer_(.exe)-2ea44f?style=for-the-badge&logo=windows&logoColor=white" alt="Download Windows Installer">
  </a>
  &nbsp;&nbsp;
  <a href="https://github.com/jayantpatel06/ytd-downloader/releases/latest/download/ytd.exe">
    <img src="https://img.shields.io/badge/Download-Portable_ytd.exe-0969da?style=for-the-badge&logo=windows&logoColor=white" alt="Download Portable EXE">
  </a>
</p>

---

## Features

- Simple desktop GUI with quality picker, destination folder selector, and progress bar
- Full CLI for terminal usage and scripting
- Video downloads up to 4K resolution
- Audio-only extraction (MP3)
- Full playlist support
- Supports YouTube and all sites supported by yt-dlp

---

## Installation

### Option 1: One-Line Terminal Command

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/jayantpatel06/ytd-downloader/main/install.ps1 | iex
```

- Automatically downloads `ytd.exe`
- Creates Desktop and Start Menu shortcuts
- Adds `ytd` to your PATH so you can use it anywhere in terminal

**Linux (Bash):**

```bash
curl -sSL https://raw.githubusercontent.com/jayantpatel06/ytd-downloader/main/install.sh | bash
```

- Automatically configures an isolated environment and installs `ytd`
- Creates an application launcher (`ytd.desktop`) in your system app menu
- Adds `ytd` command to your PATH (`~/.local/bin/ytd`)

---

### Option 2: Windows Setup Wizard (`ytd-setup.exe`)

[Download ytd-setup.exe](https://github.com/jayantpatel06/ytd-downloader/releases/latest/download/ytd-setup.exe)

- Standard Windows setup wizard
- Installs to user folder (no administrator privileges needed)
- Creates Desktop and Start Menu shortcuts
- Configures terminal PATH and Windows uninstaller

---

### Option 3: Portable Executable (`ytd.exe`)

[Download ytd.exe](https://github.com/jayantpatel06/ytd-downloader/releases/latest/download/ytd.exe)

- Single standalone executable; no installation required
- Automatically creates a Desktop shortcut on first run

---

### Option 4: Run from Source

```bash
git clone https://github.com/jayantpatel06/ytd-downloader.git
cd ytd-downloader
pip install -r requirements.txt
python -m ytd.cli          # Launch GUI
python -m ytd.cli "URL"    # CLI download
```

---

## GUI Usage

Run `ytd` or open the shortcut from your Desktop:

| Field | Description |
|-------|-------------|
| URL | Paste any video or playlist link |
| Quality | 360p, 480p, 720p, 1080p, 1440p, or 2160p (4K) |
| Download playlist | Enable to download all videos in the playlist |
| Browse | Choose destination directory (defaults to current folder) |

---

## CLI Usage

```text
ytd [URL] [options]

Options:
  -q, --quality   360|480|720|1080|1440|2160  (default: 1080)
  -o, --output    Output directory            (default: .)
  --playlist      Download entire playlist
  -a, --audio-only  Download audio only as MP3
  --gui           Launch GUI mode
  --version       Show version
  -h, --help      Show help
```

### Examples

```bash
# Launch GUI
ytd

# Download at 1080p to current folder
ytd "https://youtu.be/dQw4w9WgXcQ"

# Download at 720p to custom folder
ytd "https://youtu.be/dQw4w9WgXcQ" -q 720 -o D:\Videos

# Download audio only
ytd "https://youtu.be/dQw4w9WgXcQ" -a

# Download playlist
ytd "https://youtube.com/playlist?list=PLXXX" --playlist -o D:\Playlists
```

---

## Building from Source

To compile the standalone executable locally:

```bash
pip install pyinstaller pillow pywin32
python build_exe.py
```

The compiled binary will be placed at `dist/ytd.exe`.

---

## License

[MIT](LICENSE)
