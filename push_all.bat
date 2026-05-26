@echo off
cd /d "%~dp0"
echo # yheyue >> README.md
call Tao-lai-Shortcut-lnk.cmd
git init
git add .
git commit -m "first commit"
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/tiiisiet65-sudo/yheyue.git
git push -u origin main -f
echo.
echo Da push thanh cong len tiiisiet65-sudo/yheyue.
pause
