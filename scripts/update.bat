echo off
pybabel extract -o "%CD%/apc/locale/apc.pot" -F "%CD%\apc\babel.cfg" -k translate apc
pybabel update --domain=apc -d "%CD%\apc\locale" -i "%CD%\apc\locale\apc.pot" --no-fuzzy-matching

pybabel extract -o "%CD%/apcgui/locale/apcgui.pot" -F "%CD%\apcgui\babel.cfg" -k translate apcgui
pybabel update --domain=apcgui -d "%CD%\apcgui\locale" -i "%CD%\apcgui\locale\apcgui.pot" --no-fuzzy-matching