@echo off

cls

echo "-----------------------------------------------"
echo "               Uploading Activity              "
echo "-----------------------------------------------"
echo "         WARNING: DO NOT CLOSE THIS WINDOW     "
echo "-----------------------------------------------"

REM Set the path to the main.py file in the current folder where the batch file is located
set "main_py=%~dp0main.py"


REM Execute the Python script using the main.py file from the current folder
python "%main_py%" %*

if errorlevel 1 (
    echo "Python script failed with error code 1"
    exit /b 1
)