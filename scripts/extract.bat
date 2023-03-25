echo off
pybabel extract -o %CD%/apc/locale/apc.pot -F %CD%\apc\babel.cfg -k translate apc
pybabel extract -o %CD%/apcgui/locale/apcgui.pot -F %CD%\apcgui\babel.cfg -k translate apcgui