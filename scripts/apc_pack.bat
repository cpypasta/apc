echo off
del /s /q "%CD%\dist\package\apc"
rmdir /s /q "%CD%\dist\package\apc"
md "%CD%\dist\package\apc
copy "%CD%\dist\apc.exe" "%CD%\dist\package\apc"

del /q "%CD%\dist\apc.zip"
"C:\Program Files\7-Zip\7z.exe" a -tzip "%CD%\dist\apc.zip" "%CD%\dist\package\apc\*"

del /q "%CD%\dist\wheel.zip"
"C:\Program Files\7-Zip\7z.exe" a -tzip "%CD%\dist\wheel.zip" "%CD%\dist\*.whl"