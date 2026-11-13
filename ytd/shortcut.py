"""
ytd/shortcut.py — Creates a desktop shortcut on Windows when the exe first runs.
Works both when running as a PyInstaller-bundled exe and from source.
"""

import os
import sys


def get_exe_path() -> str:
    """Return the path to the running exe (or script in dev mode)."""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        return sys.executable
    # Running from source — point to cli.py
    return os.path.abspath(__file__.replace("shortcut.py", "cli.py"))


def get_desktop_path() -> str:
    """Return the user's Desktop folder path."""
    return os.path.join(os.path.expanduser("~"), "Desktop")


def shortcut_exists() -> bool:
    desktop = get_desktop_path()
    lnk = os.path.join(desktop, "YouTube Downloader.lnk")
    return os.path.exists(lnk)


def create_desktop_shortcut(icon_path: str = "") -> bool:
    """
    Create a Windows desktop shortcut (.lnk) pointing to this exe.
    Returns True on success, False on failure (non-Windows or error).
    """
    if os.name != "nt":
        return False  # Only Windows

    try:
        import winreg  # noqa: F401 — confirm we're on Windows
        from win32com.shell import shell  # noqa: F401

        import pythoncom
        from win32com.client import Dispatch

        desktop = get_desktop_path()
        lnk_path = os.path.join(desktop, "YouTube Downloader.lnk")
        exe_path = get_exe_path()

        shell_obj = Dispatch("WScript.Shell")
        shortcut = shell_obj.CreateShortCut(lnk_path)
        shortcut.TargetPath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.Description = "YouTube Downloader — powered by yt-dlp"

        if icon_path and os.path.exists(icon_path):
            abs_icon = os.path.abspath(icon_path)
            shortcut.IconLocation = f"{abs_icon},0"
        elif getattr(sys, "frozen", False):
            # Use the exe itself as icon source (it has the embedded icon)
            shortcut.IconLocation = f"{exe_path},0"

        shortcut.save()
        return True

    except Exception:
        # Fallback: use PowerShell to create the shortcut (no pywin32 needed)
        return _create_shortcut_powershell(icon_path)


def _create_shortcut_powershell(icon_path: str = "") -> bool:
    """Fallback shortcut creator using PowerShell — no extra dependencies."""
    import subprocess

    exe_path = get_exe_path()
    desktop = get_desktop_path()
    lnk_path = os.path.join(desktop, "YouTube Downloader.lnk")
    work_dir = os.path.dirname(exe_path)

    lnk_esc = lnk_path.replace("'", "''")
    exe_esc = exe_path.replace("'", "''")
    work_esc = work_dir.replace("'", "''")
    icon_arg = f"$s.IconLocation = '{exe_esc},0'"
    if icon_path and os.path.exists(icon_path):
        icon_esc = os.path.abspath(icon_path).replace("'", "''")
        icon_arg = f"$s.IconLocation = '{icon_esc},0'"

    ps_script = (
        f"$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{lnk_esc}'); "
        f"$s.TargetPath = '{exe_esc}'; "
        f"$s.WorkingDirectory = '{work_esc}'; "
        f"$s.Description = 'YouTube Downloader'; "
        f"{icon_arg}; "
        f"$s.Save()"
    )

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True, timeout=15,
        )
        return result.returncode == 0
    except Exception:
        return False


def ensure_shortcut(icon_path: str = "", force: bool = False) -> None:
    """Create shortcut on first run (skip if already exists unless force=True)."""
    if not force and shortcut_exists():
        return
    create_desktop_shortcut(icon_path)

