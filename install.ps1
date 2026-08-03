# Mozhi Package Manager — Windows installer (PowerShell)
#
# Usage:
#   irm https://github.com/crossberry-in/mozhi-pkg/raw/main/install.ps1 | iex
#

$ErrorActionPreference = "Stop"

$Repo = "crossberry-in/mozhi-pkg"
$InstallDir = "$env:USERPROFILE\.mozhi\bin"
$BinaryName = "mozhi"

function Write-Info    { param([string]$Msg) Write-Host "[info]  $Msg" -ForegroundColor Cyan }
function Write-OK      { param([string]$Msg) Write-Host "[ok]    $Msg" -ForegroundColor Green }
function Write-Warn    { param([string]$Msg) Write-Host "[warn]  $Msg" -ForegroundColor Yellow }
function Write-Err     { param([string]$Msg) Write-Host "[error] $Msg" -ForegroundColor Red }

Write-Host ""
Write-Host "  ===================================" -ForegroundColor Cyan
Write-Host "   Mozhi Package Manager Installer (Windows)" -ForegroundColor Cyan
Write-Host "  ===================================" -ForegroundColor Cyan
Write-Host ""

# --- Check Python -------------------------------------------------------

$PythonBin = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($LASTEXITCODE -eq 0 -and $version) {
            $parts = $version.Split(".")
            $major = [int]$parts[0]
            $minor = [int]$parts[1]
            if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 8)) {
                $PythonBin = $cmd
                Write-Info "Using Python $version ($cmd)"
                break
            }
        }
    } catch { }
}

if (-not $PythonBin) {
    Write-Err "Python 3.8+ is required but not found."
    Write-Err "Install from https://python.org"
    exit 1
}

# --- Download -----------------------------------------------------------

$DownloadUrl = "https://raw.githubusercontent.com/$Repo/main/mozhi"
$TmpFile = [System.IO.Path]::GetTempFileName()

Write-Info "Downloading mozhi CLI..."
try {
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $TmpFile -UseBasicParsing
} catch {
    Write-Err "Download failed: $_"
    exit 1
}

# --- Install ------------------------------------------------------------

Write-Info "Installing to $InstallDir..."
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
$FinalPath = Join-Path $InstallDir $BinaryName
Move-Item -Path $TmpFile -Destination $FinalPath -Force

# Create a .cmd wrapper so 'mozhi' works in CMD and PowerShell
$CmdWrapper = "$InstallDir\mozhi.cmd"
@"
@echo off
$PythonBin "%~dp0mozhi" %*
"@ | Set-Content -Path $CmdWrapper -Encoding ASCII

# Also rename the downloaded script to mozhi.py for clarity
Rename-Item -Path $FinalPath -NewName "mozhi.py" -ErrorAction SilentlyContinue

# --- Add to PATH --------------------------------------------------------

$PathEnv = [Environment]::GetEnvironmentVariable("Path", "User")
if ($PathEnv -notlike "*$InstallDir*") {
    Write-Info "Adding $InstallDir to user PATH..."
    [Environment]::SetEnvironmentVariable("Path", "$PathEnv;$InstallDir", "User")
    $env:Path = "$env:Path;$InstallDir"
} else {
    Write-Info "$InstallDir is already on the user PATH."
}

# --- Verify -------------------------------------------------------------

Write-Info "Verifying installation..."
& $PythonBin "$InstallDir\mozhi.py" version
if ($LASTEXITCODE -eq 0) {
    Write-OK "mozhi-pkg is installed and working!"
} else {
    Write-Warn "mozhi was installed but verification failed."
    Write-Warn "Open a NEW PowerShell window and run: mozhi version"
}

Write-Host ""
Write-OK "Done! For docs, visit: https://github.com/crossberry-in/mozhi-pkg"
Write-Host ""
Write-Info "Quick start:"
Write-Info "  mozhi init --lib mylib   # create a library"
Write-Info "  mozhi init --bin myapp   # create an application"
Write-Host ""
Write-Warn "Note: Open a NEW PowerShell window for 'mozhi' to be on your PATH."
