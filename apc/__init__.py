import gettext
import locale
import sys
from pathlib import Path

LOCALE_PATH = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)) / "locale/"
default_locale, _ = locale.getdefaultlocale()
t = gettext.translation("apc", localedir=LOCALE_PATH, languages=["en_US"])

__app_name__ = "apc"
__version__ = "0.2.1"