# install.ps1 — One-line web installer for YouTube Downloader
# Usage:
#   irm https://raw.githubusercontent.com/jayantpatel06/ytd-downloader/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$repo = "jayantpatel06/ytd-downloader"
$installDir = "$env:LOCALAPPDATA\Programs\YTD"
$exePath = "$installDir\ytd.exe"
$iconPath = "$installDir\ytd_icon.ico"
$desktop = [Environment]::GetFolderPath("Desktop")
$startMenu = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   Installing YouTube Downloader (YTD)       " -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Ensure install folder exists
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

# 2. Download latest ytd.exe from GitHub Releases
$downloadUrl = "https://github.com/$repo/releases/latest/download/ytd.exe"
$iconUrl = "https://raw.githubusercontent.com/$repo/main/assets/ytd_icon.ico"

Write-Host "⬇️  Downloading ytd.exe..." -ForegroundColor Yellow
$wc = New-Object System.Net.WebClient
try {
    $wc.DownloadFile($downloadUrl, $exePath)
    Write-Host "✅ Downloaded ytd.exe" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to download ytd.exe from: $downloadUrl" -ForegroundColor Red
    Write-Host "Make sure a GitHub Release with 'ytd.exe' exists in $repo" -ForegroundColor Red
    exit 1
}

# 3. Download icon
try {
    $wc.DownloadFile($iconUrl, $iconPath)
} catch {
    # Icon download failure is not fatal
}

# 4. Create Desktop & Start Menu Shortcuts
$ws = New-Object -ComObject WScript.Shell

# Desktop shortcut
$shortcutDesktop = $ws.CreateShortcut("$desktop\YouTube Downloader.lnk")
$shortcutDesktop.TargetPath = $exePath
$shortcutDesktop.WorkingDirectory = $installDir
$shortcutDesktop.Description = "YouTube Downloader"
if (Test-Path $iconPath) {
    $shortcutDesktop.IconLocation = "$iconPath,0"
}
$shortcutDesktop.Save()

# Start Menu shortcut
$shortcutStart = $ws.CreateShortcut("$startMenu\YouTube Downloader.lnk")
$shortcutStart.TargetPath = $exePath
$shortcutStart.WorkingDirectory = $installDir
$shortcutStart.Description = "YouTube Downloader"
if (Test-Path $iconPath) {
    $shortcutStart.IconLocation = "$iconPath,0"
}
$shortcutStart.Save()
Write-Host "✅ Created Desktop and Start Menu shortcuts" -ForegroundColor Green

# 5. Add to User PATH so 'ytd' command works anywhere in terminal
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$installDir*") {
    $newPath = "$currentPath;$installDir".Trim(';')
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    $env:Path = "$env:Path;$installDir"
    Write-Host "✅ Added 'ytd' to your terminal PATH" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host "👉 You can open 'YouTube Downloader' from your Desktop or Start Menu."
Write-Host "👉 Or type 'ytd' in any new Command Prompt or PowerShell window." -ForegroundColor Cyan
