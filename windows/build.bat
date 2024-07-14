@echo off
setlocal

:: Define the paths and names
set SCRIPT_NAME=app.py
set FILE_NAME="D&S ParGenerator"
set EXE_NAME=%FILE_NAME%&".exe"
set DIST_DIR="%~dp0dist"
set TARGET_PATH=%DIST_DIR%\%EXE_NAME%
set SHORTCUT_NAME="D&S ParGenerator.lnk"
set DESKTOP_PATH="%USERPROFILE%\Desktop"

:: Step 1: Package the application with PyInstaller
echo Packaging the application with PyInstaller...
pyinstaller --onefile --windowed %SCRIPT_NAME% --name=%FILE_NAME%
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller failed. Exiting.
    exit /b 1
)

:: Step 2: Create the VBS script to create the shortcut
echo Creating the VBS script...
echo Set oWS = WScript.CreateObject("WScript.Shell") > create_shortcut.vbs
echo sLinkFile = "%DESKTOP_PATH%\%SHORTCUT_NAME%" >> create_shortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> create_shortcut.vbs
echo oLink.TargetPath = %TARGET_PATH% >> create_shortcut.vbs
echo oLink.WorkingDirectory = %DIST_DIR% >> create_shortcut.vbs
echo oLink.Save >> create_shortcut.vbs

:: Step 3: Run the VBS script to create the shortcut
echo Creating the desktop shortcut...
cscript //nologo create_shortcut.vbs

:: Step 4: Clean up
echo Cleaning up...
del create_shortcut.vbs

echo Shortcut created on Desktop
endlocal
pause