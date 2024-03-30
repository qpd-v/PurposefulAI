@echo off

echo Installing PurposefulAI...

git clone https://github.com/qpd-v/PurposefulAI.git

cd PurposefulAI

pip install -r requirements.txt

echo Installation complete!

choice /C YN /M "Would you like to run Purposeful AI now?"

if %errorlevel% equ 1 (
start "" python main.py
exit
) else (
exit
)