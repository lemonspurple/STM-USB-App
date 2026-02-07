@echo off
REM Build Windows executable using the project's venv and PyInstaller
SETLOCAL
REM Use the virtualenv python executable to avoid relying on activation
SET PYVENV=.venv\Scripts\python.exe
IF NOT EXIST "%PYVENV%" (
  ECHO Virtualenv Python not found at %PYVENV%. Please create a venv or adjust the path.
  EXIT /B 1
)

REM Install PyInstaller if missing
"%PYVENV%" -m pip install --upgrade pip
"%PYVENV%" -m pip install pyinstaller

REM Build single-file GUI exe (no console). Adjust name/icon as needed.
"%PYVENV%" -m PyInstaller --noconsole --onefile --name "500-STM-GUI" \
  --icon=src\assets\icons\stm_symbol.ico \
  --add-data "src\assets;assets" \
  src\main.py

IF %ERRORLEVEL% NEQ 0 (
  ECHO Build failed.
  EXIT /B %ERRORLEVEL%
)

ECHO Build finished. See the "dist" folder for the exe.
ENDLOCAL
