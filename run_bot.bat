@echo off
title Mercury - ManyChat Alternative (Instagram Automation)
echo =======================================================
echo   ☿ Mercury: Automated Instagram DM & Comment Engine
echo =======================================================
echo.
echo Starting Mercury in Autonomous Polling Mode...
echo Webhook server & Dashboard available via: run_dashboard.bat
echo.
python "%~dp0poll_engine.py"
pause
