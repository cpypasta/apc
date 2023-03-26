echo off
del "%CD%\apc\config\save_path.txt"
pyinstaller --add-data "%CD%\apc\config;config" --add-data "%CD%\apc\locale;locale" "%CD%\apc.py"

del /q "%CD%\dist\apc-*"
python -m build