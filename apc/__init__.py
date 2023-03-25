import gettext
import locale
import sys
import os
from pathlib import Path

LOCALE_PATH = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)) / "locale/"
default_locale, _ = locale.getdefaultlocale()
env_language = os.environ.get("LANGUAGE")
if env_language:
  use_languages = env_language.split(':')
else:
  use_languages = [default_locale]
t = gettext.translation("apc", localedir=LOCALE_PATH, languages=[default_locale])

__app_name__ = "apc"
__version__ = "0.2.1"