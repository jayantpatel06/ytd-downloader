"""
build_exe.py — Build a standalone Windows .exe with PyInstaller.

Requirements:
    pip install pyinstaller pywin32 pillow

Usage:
    python build_exe.py

Output: dist/ytd.exe  — single file, no install required.
        On first launch it creates a Desktop shortcut automatically.
"""

import os
import subprocess
import sys

ICON_ICO = os.path.join("assets", "ytd_icon.ico")
ICON_PNG = os.path.join("assets", "ytd_icon.png")


def convert_png_to_ico():
    """Convert ytd_icon.png → ytd_icon.ico (multi-size) using Pillow."""
    try:
        from PIL import Image
        img = Image.open(ICON_PNG).convert("RGBA")
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        resized = [img.resize(s, Image.LANCZOS) for s in sizes]
        resized[0].save(ICON_ICO, format="ICO", sizes=sizes,
                        append_images=resized[1:])
        print(f"✅ Icon converted: {ICON_ICO}")
        return True
    except ImportError:
        print("⚠️  Pillow not installed — skipping PNG→ICO conversion.")
        print("   Run: pip install pillow")
        return False
    except FileNotFoundError:
        print(f"⚠️  Icon PNG not found at {ICON_PNG} — building without custom icon.")
        return False


def build():
    # Convert PNG → ICO if needed
    if not os.path.exists(ICON_ICO) and os.path.exists(ICON_PNG):
        convert_png_to_ico()

    has_icon = os.path.exists(ICON_ICO)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "ytd",
        # Keep a console window so CLI usage works; suppress it for GUI use
        # (GUI opens a Tk window, console is hidden by --noconsole on Windows
        #  only when double-clicked; it still appears in a terminal session)
        "--noconsole",          # hides the black terminal when double-clicked
        "--hidden-import", "ytd.gui",
        "--hidden-import", "ytd.cli",
        "--hidden-import", "ytd.shortcut",
        "--hidden-import", "ytd.ffmpeg_utils",
        "--hidden-import", "win32com",
        "--hidden-import", "win32com.client",
        "--hidden-import", "win32com.shell",
        "--hidden-import", "pythoncom",
        # Bundle the icon inside the exe so shortcut.py can reference it
        f"--add-data=assets{os.pathsep}assets",
    ]

    # Optional: If ffmpeg.exe exists locally in assets/ or PATH, bundle it for 100% standalone
    import shutil
    ffmpeg_local = os.path.join("assets", "ffmpeg.exe")
    if os.path.exists(ffmpeg_local):
        cmd.append(f"--add-binary={ffmpeg_local}{os.pathsep}.")
        print("Bundling local ffmpeg.exe into ytd.exe")
    elif shutil.which("ffmpeg"):
        ffmpeg_bin = shutil.which("ffmpeg")
        cmd.append(f"--add-binary={ffmpeg_bin}{os.pathsep}.")
        print(f"Bundling system ffmpeg ({ffmpeg_bin}) into ytd.exe")

    if has_icon:
        cmd += ["--icon", ICON_ICO]

    cmd.append("ytd/cli.py")

    print("Building ytd.exe...")
    print("Command:", " ".join(cmd))
    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print("\nBuild complete. Executable created at: dist/ytd.exe")
        print("First launch creates a Desktop shortcut automatically.")
    else:
        print("\nBuild failed. See output above.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    build()

