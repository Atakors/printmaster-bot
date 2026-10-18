@echo off
title PrintMaster A4 - Telegram Bot
cd /d "%~dp0\.."

echo ========================================================
echo       PrintMaster A4 - Telegram Bot Runner
echo ========================================================
echo.

python -m telegram_bot.bot

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Bot stopped with an error or token missing.
    pause
)
