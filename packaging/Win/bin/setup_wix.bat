@echo off
@REM Find WiX toolkit

set WIX_PATH="%WIX%bin"
if EXIST %WIX_PATH% (
echo "Info: WIX Toolset found on system: %WIX%"
) ELSE (
echo Info: WIX Toolset NOT found on system.
exit /B 1
) 

copy %WORKSPACE%\packaging\Win\WiX\* .