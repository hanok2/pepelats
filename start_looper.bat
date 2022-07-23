@echo off

IF not defined PEDAL_COMMANDS_PORT (
  set PEDAL_COMMANDS_PORT=PedalCommands_out
)

SET mypath=%~dp0
cd %mypath%
tasklist | FINDSTR "python.exe"
If not errorlevel 1 (GOTO :already_running)

.\..\midimappy\start_converter.bat --use_typing


GOTO :normal_exit

:already_running
echo "already running python.exe"


:normal_exit
