@echo off

cls

echo "-----------------------------------------------"
echo "               Uploading Activity              "
echo "-----------------------------------------------"
echo "         WARNING: DO NOT CLOSE THIS WINDOW     "
echo "-----------------------------------------------"


python C:\Users\2btec\PycharmProjects\UploadScript\main.py %*
if errorlevel 1 (
    echo "Python script failed with error code 1"
    pause
    exit /b 1
)
pause