echo off
del /q "%CD%\dist\apcgui.zip"
"C:\Program Files\7-Zip\7z.exe" a -tzip "%CD%\dist\apcgui.zip" "%CD%\dist\apcgui"