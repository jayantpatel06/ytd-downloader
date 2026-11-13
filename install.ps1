# install.ps1 — Web installer for YouTube Downloader
# Usage:
#   irm https://raw.githubusercontent.com/jayantpatel06/ytd-downloader/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
} catch {}

$repo = "jayantpatel06/ytd-downloader"
$installDir = "$env:LOCALAPPDATA\Programs\YTD"
$exePath = "$installDir\ytd.exe"
$iconPath = "$installDir\ytd_icon.ico"
$desktop = [Environment]::GetFolderPath("Desktop")
$startMenu = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"

Write-Host "Installing YouTube Downloader..."

# 1. Ensure install folder exists
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

# 2. Download ytd.exe
$downloadUrl = "https://github.com/$repo/releases/latest/download/ytd.exe"
$iconUrl = "https://raw.githubusercontent.com/$repo/main/assets/ytd_icon.ico"

Write-Host "- Downloading ytd.exe..."
$ProgressPreference = 'Continue'
try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $exePath -UserAgent "Mozilla/5.0 ytd-installer"
    $sizeMB = [math]::Round(((Get-Item $exePath).Length / 1MB), 1)
    Write-Host "  Saved ytd.exe ($sizeMB MB)"
} catch {
    try {
        $wc = New-Object System.Net.WebClient
        $wc.Headers.Add("User-Agent", "Mozilla/5.0 ytd-installer")
        $wc.DownloadFile($downloadUrl, $exePath)
        $sizeMB = [math]::Round(((Get-Item $exePath).Length / 1MB), 1)
        Write-Host "  Saved ytd.exe ($sizeMB MB)"
    } catch {
        Write-Host "Error: Failed to download ytd.exe from $downloadUrl" -ForegroundColor Red
        Write-Host "Please ensure a release exists in https://github.com/$repo/releases" -ForegroundColor Red
        exit 1
    }
}

# 3. Download icon
try {
    $wc = New-Object System.Net.WebClient
    $wc.Headers.Add("User-Agent", "Mozilla/5.0 ytd-installer")
    $wc.DownloadFile($iconUrl, $iconPath)
} catch {}

# 4. Create Desktop & Start Menu Shortcuts
$ws = New-Object -ComObject WScript.Shell

$shortcutDesktop = $ws.CreateShortcut("$desktop\YouTube Downloader.lnk")
$shortcutDesktop.TargetPath = $exePath
$shortcutDesktop.WorkingDirectory = $installDir
$shortcutDesktop.Description = "YouTube Downloader"
if (Test-Path $iconPath) {
    $shortcutDesktop.IconLocation = "$iconPath,0"
} else {
    $shortcutDesktop.IconLocation = "$exePath,0"
}
$shortcutDesktop.Save()

$shortcutStart = $ws.CreateShortcut("$startMenu\YouTube Downloader.lnk")
$shortcutStart.TargetPath = $exePath
$shortcutStart.WorkingDirectory = $installDir
$shortcutStart.Description = "YouTube Downloader"
if (Test-Path $iconPath) {
    $shortcutStart.IconLocation = "$iconPath,0"
} else {
    $shortcutStart.IconLocation = "$exePath,0"
}
$shortcutStart.Save()
Write-Host "- Created Desktop and Start Menu shortcuts"

# 5. Add to User PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$installDir*") {
    $newPath = "$currentPath;$installDir".Trim(';')
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    $env:Path = "$env:Path;$installDir"
    Write-Host "- Added to system PATH"
}

Write-Host ""
Write-Host "Installation complete."
Write-Host "  Location : $installDir"
Write-Host "  Shortcut : Desktop -> YouTube Downloader"
Write-Host "  Terminal : Type 'ytd' to launch"
