echo off
pybabel extract -o "%CD%/apc/locale/apc.pot" -F "%CD%\apc\babel.cfg" -k translate apc
pybabel update --domain=apc -d "%CD%\apc\locale" -i "%CD%\apc\locale\apc.pot" --no-fuzzy-matching