$ErrorActionPreference = "Stop"

$Root   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Icon   = Join-Path $Root "assets\app.ico"
$Venv   = Join-Path $Root ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"
$Dist   = Join-Path $Root "dist"
$Build  = Join-Path $Root "build\nuitka"

if (!(Test-Path -LiteralPath $Icon)) {
    throw "Missing assets\app.ico - place your icon there before building."
}

# --- install dependencies via uv ---
uv sync
uv pip install nuitka

# --- compile with Nuitka ---
if (!(Test-Path -LiteralPath $Dist)) {
    New-Item -ItemType Directory -Path $Dist | Out-Null
}

& $Python -m nuitka `
    --standalone `
    --onefile `
    --assume-yes-for-downloads `
    --windows-console-mode=disable `
    --windows-icon-from-ico=$Icon `
    --enable-plugin=tk-inter `
    --include-data-files="$Icon=assets/app.ico" `
    --output-dir=$Build `
    --output-filename="GFN Discord RPC.exe" `
    (Join-Path $Root "main.py")

$BuiltExe = Join-Path $Build "GFN Discord RPC.exe"
Copy-Item -LiteralPath $BuiltExe -Destination (Join-Path $Dist "GFN Discord RPC.exe") -Force

Write-Host "`nBuilt: dist\GFN Discord RPC.exe" -ForegroundColor Green

# --- optional: Inno Setup installer ---
$Inno = $null
foreach ($Path in @(
    (Get-Command iscc -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source),
    (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
    (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"),
    (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe")
)) {
    if ($Path -and (Test-Path -LiteralPath $Path)) {
        $Inno = $Path
        break
    }
}

if ($Inno) {
    & $Inno (Join-Path $Root "installer.iss")
    Write-Host "Built: installer\GFNDiscordRPCSetup.exe" -ForegroundColor Green
} else {
    Write-Host "Inno Setup not found - skipping installer. Install Inno Setup 6 to build the installer." -ForegroundColor Yellow
}
