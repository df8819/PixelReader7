@echo off
:: BatchGotAdmin
echo Running run.bat...
echo.
:-------------------------------------
REM --> Check for permissions
echo Verifying admin permissions...
>nul 2>&1 "%SYSTEMROOT%\system32\icacls.exe" "%SYSTEMROOT%\system32\config\system"

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Creating VBS script to obtain admin rights...
    echo.
    goto UACPrompt
) else (
    echo.
    echo Admin permissions confirmed...
    echo.
    goto gotAdmin
)

:UACPrompt
    echo Executing VBS script to request admin rights...
    echo.
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    echo VBS script created. Running script...
    echo.
    "%temp%\getadmin.vbs"
    echo Cleaning up VBS script...
    echo.
    del "%temp%\getadmin.vbs"
    echo VBS script removed. Exiting batch run.bat...
    echo.
    exit /B

:gotAdmin
    echo Admin permissions obtained. Proceeding to execute .py file...
    echo.
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------

:: Running the Python script with admin privileges
echo Starting the Python application...
echo.
python main.py
if %errorlevel% NEQ 0 (
    echo Error: Failed to execute the Python application.
    echo.
    exit /B %errorlevel%
)
echo Python application executed successfully.
echo.

:: Close the terminal window after the script finishes
exit
