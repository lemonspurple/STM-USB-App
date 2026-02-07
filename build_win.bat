@echo off
REM Build Windows executable: stop running exe, clean outputs, then build
SETLOCAL
SET PYVENV=.venv\Scripts\python.exe
IF NOT EXIST "%PYVENV%" (
  ECHO Virtualenv Python not found at %PYVENV%. Please create a venv or adjust the path.
  EXIT /B 1
)

REM Stop any running instance
tasklist /FI "IMAGENAME eq 500-STM-GUI.exe" | findstr /I "500-STM-GUI.exe" >nul
IF %ERRORLEVEL% EQU 0 (
  taskkill /IM 500-STM-GUI.exe /F >nul 2>&1
)

REM Remove previous outputs
IF EXIST dist rmdir /S /Q dist
IF EXIST build rmdir /S /Q build
IF EXIST 500-STM-GUI.spec del /F /Q 500-STM-GUI.spec

REM Ensure pyinstaller is available
"%PYVENV%" -m pip install --upgrade pip
"%PYVENV%" -m pip install pyinstaller

REM Build single-file GUI exe (no console). Adjust name/icon as needed.
"%PYVENV%" -m PyInstaller --noconsole --onefile --paths=src --name "500-STM-GUI" ^
  --icon=src\assets\icons\stm_symbol.ico ^
  --add-data "src\assets;assets" ^
  src\main.py

IF %ERRORLEVEL% NEQ 0 (
  ECHO Build failed.
  EXIT /B %ERRORLEVEL%
)

ECHO Build finished. See the "dist" folder for the exe.
ENDLOCAL
