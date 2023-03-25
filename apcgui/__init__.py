import gettext
import locale
import sys
from pathlib import Path

LOCALE_PATH = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)) / "locale/"
default_locale, _ = locale.getdefaultlocale()
tgui = gettext.translation("apcgui", localedir=LOCALE_PATH, languages=["en_DE"])

__app_name__ = "apcgui"
__version__ = "0.2.1"