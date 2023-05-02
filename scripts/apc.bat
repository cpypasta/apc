echo off
del "%CD%\apc\config\save_path.txt"

del /q "%CD%\dist\apc-*"
python -m build