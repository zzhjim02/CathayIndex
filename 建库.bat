@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
set "PYEXE="

if exist "%~dp0runtime\python.exe" (
  "%~dp0runtime\python.exe" -c "import tkinter" >nul 2>&1 && set "PYEXE=%~dp0runtime\python.exe"
)

if not defined PYEXE (
  py -3 -c "import tkinter" >nul 2>&1 && set "PYEXE=py -3"
)
if not defined PYEXE (
  python -c "import tkinter" >nul 2>&1 && set "PYEXE=python"
)
if not defined PYEXE (
  for %%D in (
    "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
    "%ProgramFiles%\Python310\python.exe"
    "%ProgramFiles%\Python311\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
  ) do (
    if exist %%D (
      %%D -c "import tkinter" >nul 2>&1 && set "PYEXE=%%D"
    )
  )
)

if not defined PYEXE (
  echo.
  echo Python with tkinter was not found on this machine.
  echo Install Python 3.10+ ^(tkinter included^), then run this file again.
  echo.
  pause
  exit /b 1
)

if "%~1"=="--selftest" (
  %PYEXE% "%~dp0gui.py" --selftest
  echo.
  echo selftest written to _selftest.txt
  goto :eof
)

%PYEXE% "%~dp0gui.py"
goto :eof
