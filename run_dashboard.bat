@echo off
title Mercury Dashboard & Automation Server
echo =====================================================================
echo   ☿ Mercury: 2D Gallery Dashboard & Meta Automation Server (FastAPI)
echo =====================================================================
echo.
echo Launching Mercury server on http://localhost:8000 ...
echo Opening your browser to the Aesthetic 2D Dashboard...
echo.

start "" "http://localhost:8000/"
python "%~dp0server.py"
pause
