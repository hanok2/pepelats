@echo off

echo %homedrive%%homepath%\midimappy\start_converter.bat
%homedrive%%homepath%\midimappy\start_converter.bat

exit 1

IF not defined PEDAL_COMMANDS_PORT (
  set PEDAL_COMMANDS_PORT=PedalCommands_out
)

SET mypath=%~dp0
cd %mypath%
tasklist | FINDSTR "python.exe"
If not errorlevel 1 (GOTO :already_running)

c:\apps\py39\python.exe .\start_converter.py %*

GOTO :normal_exit

:already_running
echo "already running python.exe"


:normal_exit
