Write-Host "Preparing build: stopping running exe and cleaning outputs..."

$py = Join-Path -Path $PSScriptRoot -ChildPath ".venv\Scripts\python.exe"
if (-Not (Test-Path $py)) {
    Write-Error "Virtualenv python not found at $py. Create a venv or adjust the path."
    exit 1
}

# Stop running instances (if any) and remove previous build outputs
try {
    Get-Process -Name 500-STM-GUI -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
} catch {
    # ignore
}

try {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $PSScriptRoot 'dist')
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $PSScriptRoot 'build')
    Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $PSScriptRoot '500-STM-GUI.spec')
} catch {
    # ignore
}

Write-Host "Building Windows exe using venv and PyInstaller..."

& $py -m pip install --upgrade pip
& $py -m pip install pyinstaller

& $py -m PyInstaller --noconsole --onefile --paths=src --name "500-STM-GUI" `
    --icon=src\assets\icons\stm_symbol.ico `
    --add-data "src\assets;assets" `
    src\main.py

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed"
    exit $LASTEXITCODE
}

Write-Host "Build finished. See the 'dist' folder for the exe."
