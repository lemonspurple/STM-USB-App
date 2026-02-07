Write-Host "Building Windows exe using venv and PyInstaller..."
$py = Join-Path -Path $PSScriptRoot -ChildPath ".venv\Scripts\python.exe"
if (-Not (Test-Path $py)) {
    Write-Error "Virtualenv python not found at $py. Create a venv or adjust the path."
    exit 1
}

& $py -m pip install --upgrade pip
& $py -m pip install pyinstaller

& $py -m PyInstaller --noconsole --onefile --name "500-STM-GUI" `
    --icon=src\assets\icons\stm_symbol.ico `
    --add-data "src\assets;assets" `
    src\main.py

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed"
    exit $LASTEXITCODE
}

Write-Host "Build finished. See the 'dist' folder for the exe."
