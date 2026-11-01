@echo off
setlocal
pushd "%~dp0" || exit /b 1

if exist ".venv\Scripts\python.exe" goto check_environment

where py >nul 2>nul
if errorlevel 1 goto use_python_command
py -3 -c "import sys; raise SystemExit(sys.version_info < (3, 10))" >nul 2>nul
if errorlevel 1 goto use_python_command
py -3 -m venv .venv
if errorlevel 1 goto venv_creation_failed
goto check_environment

:use_python_command
where python >nul 2>nul
if errorlevel 1 goto python_missing
python -c "import sys; raise SystemExit(sys.version_info < (3, 10))" >nul 2>nul
if errorlevel 1 goto python_missing
python -m venv .venv
if errorlevel 1 goto venv_creation_failed

:check_environment
".venv\Scripts\python.exe" -c "import sys; raise SystemExit(sys.version_info < (3, 10))" >nul 2>nul
if errorlevel 1 (
    echo The project's .venv must use Python 3.10 or newer.
    echo Delete only the .venv folder and run this launcher again.
    goto failed
)

".venv\Scripts\python.exe" -c "import pathlib, pygame, spacedefender; assert pathlib.Path(spacedefender.__file__).resolve().parent == pathlib.Path('src/spacedefender').resolve()" >nul 2>nul
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -e .
    if errorlevel 1 (
        echo Could not install the game or its dependencies.
        goto failed
    )
    ".venv\Scripts\python.exe" -c "import pathlib, pygame, spacedefender; assert pathlib.Path(spacedefender.__file__).resolve().parent == pathlib.Path('src/spacedefender').resolve()" >nul 2>nul
    if errorlevel 1 (
        echo The game could not be loaded from this project folder.
        goto failed
    )
)

".venv\Scripts\python.exe" -m spacedefender
set "GAME_EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %GAME_EXIT_CODE%

:python_missing
echo Python 3.10 or newer is required. Install Python and try again.
goto failed

:venv_creation_failed
echo Could not create the virtual environment.

:failed
popd
exit /b 1
