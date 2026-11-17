@echo off
chcp 65001 >nul
echo ========================================================
echo   DANG DAY TOAN BO DASHBOARD LEN GITHUB: bao_cao_team4
echo ========================================================
echo.

set "GIT_EXE=C:\Users\hungnv\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe"

cd /d "D:\Báo cáo"

echo Dang kiem tra trang thai Git...
"%GIT_EXE%" status

echo.
echo Dang day len GitHub (https://github.com/developer2605/bao_cao_team4)...
echo (Neu trinh duyet bat len yeu cau dang nhap GitHub, ban chi can bam Dong y / Authorize)
echo.

"%GIT_EXE%" push -u origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================================
    echo   DA DAY LEN GITHUB THANH CONG!
    echo   Xem repo tai: https://github.com/developer2605/bao_cao_team4
    echo ========================================================
) else (
    echo ========================================================
    echo   CO LOI XAY RA KHI PUSH!
    echo   Luu y:
    echo   1. Hay dam bao ban da tao repo 'bao_cao_team4' tren GitHub:
    echo      https://github.com/new
    echo   2. Dang nhap tai khoan developer2605 khi trinh duyet hoi.
    echo ========================================================
)

echo.
pause
