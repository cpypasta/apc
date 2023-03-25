echo off
pybabel compile --domain=apc --directory="%CD%\apc\locale"
pybabel compile --domain=apcgui --directory="%CD%\apcgui\locale"