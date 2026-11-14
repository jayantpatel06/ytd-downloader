#!/usr/bin/env bash
# install.sh — Web & local installer for YouTube Downloader on Linux
# Usage:
#   curl -sSL https://raw.githubusercontent.com/jayantpatel06/ytd-downloader/main/install.sh | bash

set -e

REPO="jayantpatel06/ytd-downloader"
INSTALL_DIR="$HOME/.local/share/ytd"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_PATH="$INSTALL_DIR/ytd_icon.png"

echo "============================================="
echo "   Installing YouTube Downloader for Linux   "
echo "============================================="

# 1. Ensure Python 3 is installed
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is required but not installed." >&2
    echo "Install it via your package manager (e.g. sudo apt install python3)" >&2
    exit 1
fi

# 2. Check for FFmpeg (auto-downloaded on first run if missing from system)
if command -v ffmpeg &>/dev/null || [ -f "$INSTALL_DIR/bin/ffmpeg" ]; then
    echo "- FFmpeg media engine: OK"
else
    echo "- FFmpeg not detected in system PATH; ytd will automatically set up a static binary on first run."
fi

# 3. Create target directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"

# 4. Create isolated virtual environment
echo "- Setting up isolated Python environment in $INSTALL_DIR/venv..."
if ! python3 -m venv "$INSTALL_DIR/venv" 2>/dev/null; then
    echo "Error: Failed to create Python virtual environment." >&2
    echo "On Debian/Ubuntu, please install python3-venv first:" >&2
    echo "    sudo apt update && sudo apt install -y python3-venv python3-pip" >&2
    exit 1
fi

# 5. Install ytd-downloader into the venv
VENV_PIP="$INSTALL_DIR/venv/bin/pip"
VENV_PYTHON="$INSTALL_DIR/venv/bin/python"

echo "- Installing ytd-downloader..."
"$VENV_PIP" install --upgrade pip setuptools wheel --quiet

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"
if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    "$VENV_PIP" install "$SCRIPT_DIR" --quiet
    if [ -f "$SCRIPT_DIR/assets/ytd_icon.png" ]; then
        cp "$SCRIPT_DIR/assets/ytd_icon.png" "$ICON_PATH"
    fi
else
    "$VENV_PIP" install "git+https://github.com/$REPO.git" --quiet
    ICON_URL="https://raw.githubusercontent.com/$REPO/main/assets/ytd_icon.png"
    if command -v curl &>/dev/null; then
        curl -sSL "$ICON_URL" -o "$ICON_PATH" 2>/dev/null || true
    elif command -v wget &>/dev/null; then
        wget -qO "$ICON_PATH" "$ICON_URL" 2>/dev/null || true
    fi
fi

# 6. Create terminal launcher wrapper in ~/.local/bin/ytd
cat << EOF > "$BIN_DIR/ytd"
#!/usr/bin/env bash
exec "$INSTALL_DIR/venv/bin/ytd" "\$@"
EOF
chmod +x "$BIN_DIR/ytd"
echo "- Installed CLI command to $BIN_DIR/ytd"

# 7. Create desktop menu launcher entry & Desktop screen shortcut
cat << EOF > "$DESKTOP_DIR/ytd.desktop"
[Desktop Entry]
Name=YouTube Downloader
Comment=Fast, minimal video and audio downloader powered by yt-dlp
Exec=$BIN_DIR/ytd %U
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=AudioVideo;Video;Network;
EOF
chmod +x "$DESKTOP_DIR/ytd.desktop"
echo "- Created App Menu launcher: $DESKTOP_DIR/ytd.desktop"

# Also place on user's Desktop folder if it exists
if [ -d "$HOME/Desktop" ]; then
    cp "$DESKTOP_DIR/ytd.desktop" "$HOME/Desktop/ytd.desktop"
    chmod +x "$HOME/Desktop/ytd.desktop" 2>/dev/null || true
    if command -v gio &>/dev/null; then
        gio set "$HOME/Desktop/ytd.desktop" metadata::trusted true 2>/dev/null || true
    fi
    echo "- Created Desktop shortcut: $HOME/Desktop/ytd.desktop"
fi

# 8. Check if ~/.local/bin is in PATH
case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *)
        echo ""
        echo "[Note] $BIN_DIR is not yet in your PATH."
        echo "To run 'ytd' from anywhere, add this line to your ~/.bashrc or ~/.zshrc:"
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
        ;;
esac

echo ""
echo "Installation complete!"
echo "  Location : $INSTALL_DIR"
echo "  Launcher : Applications Menu -> YouTube Downloader"
echo "  Terminal : Type 'ytd' to launch"

