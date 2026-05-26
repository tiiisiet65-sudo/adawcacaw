@echo off
setlocal
REM Luon chay script trong cung thu muc voi file .cmd nay (ke ca khi copy sang o/may khac).
cd /d "%~dp0"

echo.
echo [Chay-Tai-macOSx] Thu muc: %CD%
echo.

where powershell.exe >nul 2>&1
if errorlevel 1 (
    echo LOI: Khong tim thay powershell.exe trong PATH.
    goto :end
)

if not exist "%~dp0restore-macOSx-from-github.ps1" (
    echo LOI: Khong tim thay file: restore-macOSx-from-github.ps1
    echo Hay chay file .cmd nay ngay trong thu muc da copy (khong dung shortcut cu tu may khac).
    goto :end
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Normal -File "%~dp0restore-macOSx-from-github.ps1"
set ERR=%ERRORLEVEL%

echo.
if %ERR% neq 0 (
    echo PowerShell thoat voi ma loi: %ERR%
) else (
    echo PowerShell thoat binh thuong: 0
)

:end
echo.
pause
