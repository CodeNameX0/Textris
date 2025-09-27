@echo off
chcp 65001 >nul
color 0F
title TEXTRIS - 텍스트 테트리스 게임

cd /d "%~dp0"

echo.
echo ==========================================
echo =                                        =
echo =        TEXTRIS 게임 시작               =
echo =      텍스트 테트리스 게임               =
echo =                                        =
echo ==========================================
echo.
echo 조작법:
echo   왼쪽/오른쪽 화살표키 : 좌우 이동
echo   아래쪽 화살표키 : 빠른 낙하
echo   위쪽 화살표키 또는 스페이스바 : 회전
echo   Enter키 : 일시정지/재개
echo   R키 : 재시작
echo   ESC키 : 종료
echo.
echo 게임을 시작합니다...
timeout /t 3 /nobreak >nul

.venv\Scripts\python.exe textris.py

echo.
echo 게임이 종료되었습니다.
echo 아무 키나 눌러 창을 닫으세요.
pause >nul
