<# :
@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-Expression (Get-Content -Raw '%~f0')"
pause
goto :EOF
#>
Write-Host "Hello from D:\Downloads\lnk"
