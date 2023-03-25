echo off
del /s /q "%CD%\dist\package\apc"
rmdir /s /q "%CD%\dist\package\apc"
md "%CD%\dist\package\apc\mods"
copy "%CD%\dist\apcgui.exe" "%CD%\dist\package\apc"

del /q "%CD%\dist\apcgui.zip"
"C:\Program Files\7-Zip\7z.exe" a -tzip "%CD%\dist\apcgui.zip" "%CD%\dist\package\apc\"