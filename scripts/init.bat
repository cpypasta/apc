echo off
pybabel init -l en_DE -i "%CD%\apc\locale\apc.pot" -d "%CD%\apc\locale" -D apc
pybabel init -l en_US -i "%CD%\apc\locale\apc.pot" -d "%CD%\apc\locale" -D apc