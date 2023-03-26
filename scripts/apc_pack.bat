echo off
del /q "%CD%\dist\apc.zip"
"C:\Program Files\7-Zip\7z.exe" a -tzip "%CD%\dist\apc.zip" "%CD%\dist\apc\"

del /q "%CD%\dist\wheel.zip"
"C:\Program Files\7-Zip\7z.exe" a -tzip "%CD%\dist\wheel.zip" "%CD%\dist\*.whl"