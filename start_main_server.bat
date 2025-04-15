@echo off
set PORT=%1
if "%PORT%"=="" set PORT=5555
echo Starting Chess Online Server on port %PORT%...
python server.py --port %PORT%
pause 