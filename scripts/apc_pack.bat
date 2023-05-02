echo off
del /q "%CD%\dist\wheel.7z"
"C:\Program Files\7-Zip\7z.exe" a "%CD%\dist\wheel.7z" "%CD%\dist\*.whl"