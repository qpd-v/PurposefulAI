@echo off

echo Installing PurposefulAI...

git clone https://github.com/qpd-v/PurposefulAI.git
cd PurposefulAI
pip install -r requirements.txt

echo Installation complete!
pause
