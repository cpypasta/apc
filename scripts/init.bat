echo off
pybabel init -l de_DE -i "%CD%\apc\locale\apc.pot" -d "%CD%\apc\locale" -D apc
pybabel init -l en_US -i "%CD%\apc\locale\apc.pot" -d "%CD%\apc\locale" -D apc

pybabel init -l de_DE -i "%CD%\apcgui\locale\apcgui.pot" -d "%CD%\apcgui\locale" -D apcgui
pybabel init -l en_US -i "%CD%\apcgui\locale\apcgui.pot" -d "%CD%\apcgui\locale" -D apcgui