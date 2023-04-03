echo off
pyinstaller --noconsole --add-data "%CD%\apc\config;config" --add-data "%CD%\apc\locale;locale" apcgui.py