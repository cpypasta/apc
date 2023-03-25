echo off
del "%CD%\apc\config\save_path.txt"
pyinstaller -F --add-data "%CD%\apc\config;config" --add-data "%CD%\apc\locale;locale" "%CD%\apc.py"