echo off
del /q "%CD%\dist\apcgui.7z"
"C:\Program Files\7-Zip\7z.exe" a "%CD%\dist\apcgui.7z" "%CD%\dist\apcgui"