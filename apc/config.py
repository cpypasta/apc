import os
import re
import json
import sys
import locale
import gettext
from pathlib import Path
from enum import Enum
from apc import __app_name__
from typing import List

SUPPORTED_LANGUAGES = ["en_US", "de_DE", "zh_CN", "ru_RU", "es_ES"]
default_locale = None

def get_languages() -> list:
  global default_locale
  default_locale, _ = locale.getdefaultlocale()
  env_language = os.environ.get("LANGUAGE")
  global use_languages
  if env_language:
    use_languages = env_language.split(':')
  else:
    use_languages = [default_locale]
  
  use_languages = list(filter(lambda x: x in SUPPORTED_LANGUAGES, use_languages))  
  if len(use_languages) == 0:
    use_languages = ["en_US"]
    
  return (default_locale, use_languages)

LOCALE_PATH = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)) / "locale/"
_default, use_languages = get_languages()
t = gettext.translation("apc", localedir=LOCALE_PATH, languages=use_languages)
translate = t.gettext

def setup_translations() -> None:
  global APC 
  APC = translate("Animal Population Changer")
  global SPECIES
  SPECIES = translate("Species")
  global ANIMALS_TITLE
  ANIMALS_TITLE = translate("Animals")
  global MALE
  MALE = translate("Male")
  global MALES
  MALES = translate("Males")
  global FEMALE
  FEMALE = translate("Female")
  global FEMALES
  FEMALES = translate("Females")
  global HIGH_WEIGHT
  HIGH_WEIGHT = translate("High Weight")
  global HIGH_SCORE
  HIGH_SCORE = translate("High Score")
  global LEVEL
  LEVEL = translate("Level")
  global GENDER
  GENDER = translate("Gender")
  global WEIGHT
  WEIGHT = translate("Weight")
  global SCORE
  SCORE = translate("Score")
  global VISUALSEED
  VISUALSEED = translate("Visual Seed")
  global FUR
  FUR = translate("Fur")
  global DIAMOND
  DIAMOND = translate("Diamond")
  global GREATONE
  GREATONE = translate("Great One")
  global SUMMARY
  SUMMARY = translate("Summary")
  global RESERVE
  RESERVE = translate("Reserve")
  global RESERVES_TITLE
  RESERVES_TITLE = translate("Reserves")
  global RESERVE_NAME_KEY
  RESERVE_NAME_KEY = translate("Reserve Name (key)")
  global YES
  YES = translate("Yes")
  global MODDED
  MODDED = translate("Modded")
  global SPECIES_NAME_KEY
  SPECIES_NAME_KEY = translate("Species (key)")
  global VIEWING_MODDED
  VIEWING_MODDED = translate("viewing modded")
  global NEW_BUG
  NEW_BUG = translate("Please copy and paste as a new bug on Nexusmods here")
  global ERROR
  ERROR = translate("Error")
  global UNEXPECTED_ERROR
  UNEXPECTED_ERROR = translate("Unexpected Error")
  global WARNING
  WARNING = translate("Warning")
  global SAVED
  SAVED = translate("Saved")
  global DOES_NOT_EXIST
  DOES_NOT_EXIST = translate("does not exist")
  global FAILED_TO_BACKUP
  FAILED_TO_BACKUP = translate("failed to backup game")
  global FAILED_TO_LOAD_BACKUP
  FAILED_TO_LOAD_BACKUP = translate("failed to load backup file")
  global FAILED_TO_LOAD_MOD
  FAILED_TO_LOAD_MOD = translate("failed to load mod")
  global FAILED_TO_UNLOAD_MOD
  FAILED_TO_UNLOAD_MOD = translate("failed to unload mod")
  global MOD_LOADED
  MOD_LOADED = translate("Mod has been loaded")
  global MOD_UNLOADED
  MOD_UNLOADED = translate("Mod has been unloaded")
  global VERSION
  VERSION = translate("Version")
  global HUNTING_RESERVE
  HUNTING_RESERVE = translate("Hunting Reserve")
  global UPDATE_BY_PERCENTAGE
  UPDATE_BY_PERCENTAGE = translate("update by percentage")
  global MORE_MALES
  MORE_MALES = translate("More Males")
  global MORE_FEMALES
  MORE_FEMALES = translate("More Females")
  global GREATONES
  GREATONES = translate("Great Ones")
  global DIAMONDS
  DIAMONDS = translate("Diamonds")
  global INCLUDE_RARE_FURS
  INCLUDE_RARE_FURS = translate("include rare furs")
  global ALL_FURS
  ALL_FURS = translate("All Furs")
  global RESET
  RESET = translate("Reset")
  global UPDATE_ANIMALS
  UPDATE_ANIMALS = translate("Update Animals")
  global JUST_FURS
  JUST_FURS = translate("Just the Furs")
  global ONE_OF_EACH_FUR
  ONE_OF_EACH_FUR = translate("one of each fur")
  global OTHERS
  OTHERS = translate("Others")
  global PARTY
  PARTY = translate("Party")
  global GREATONE_PARTY
  GREATONE_PARTY = translate("Great One Party")
  global DIAMOND_PARTY
  DIAMOND_PARTY = translate("Diamond Party")
  global WE_ALL_PARTY
  WE_ALL_PARTY = translate("We All Party")
  global FUR_PARTY
  FUR_PARTY = translate("Fur Party")
  global EXPLORE
  EXPLORE = translate("Explore")
  global DIAMONDS_AND_GREATONES
  DIAMONDS_AND_GREATONES = translate("diamonds and Great Ones")
  global LOOK_MODDED_ANIMALS
  LOOK_MODDED_ANIMALS = translate("look at modded animals")
  global LOOK_ALL_RESERVES
  LOOK_ALL_RESERVES = translate("look at all reserves")
  global ONLY_TOP_SCORES
  ONLY_TOP_SCORES = translate("only top 10 scores")
  global SHOW_ANIMALS
  SHOW_ANIMALS = translate("Show Animals")
  global FILES
  FILES = translate("Files")
  global CONFIGURE_GAME_PATH
  CONFIGURE_GAME_PATH = translate("Configure Game Path")
  global LIST_MODS
  LIST_MODS = translate("List Mods")
  global LOAD_MOD
  LOAD_MOD = translate("Load Mod")
  global UNLOAD_MOD
  UNLOAD_MOD = translate("Unload Mod")
  global SELECT_FOLDER
  SELECT_FOLDER = translate("Select the folder where the game saves your files")
  global SAVES_PATH_TITLE
  SAVES_PATH_TITLE = translate("Saves Path")
  global PATH_SAVED
  PATH_SAVED = translate("Game path saved")
  global CONFIRM_LOAD_MOD
  CONFIRM_LOAD_MOD = translate("Are you sure you want to overwrite your game file with the modded one?")
  global BACKUP_WILL_BE_MADE
  BACKUP_WILL_BE_MADE = translate("Don't worry, a backup copy will be made.")
  global CONFIRMATION
  CONFIRMATION = translate("Confirmation")
  global MOD
  MOD = translate("Mod")
  global VIEW_MODDED_VERSION
  VIEW_MODDED_VERSION = translate("view modded version")
  global LOADED
  LOADED = translate("Loaded")
  global MODDED_FILE
  MODDED_FILE = translate("Modded File")
  global BACK_TO_RESERVE
  BACK_TO_RESERVE = translate("Back to Reserve")
  global UPDATE_TRANSLATIONS
  UPDATE_TRANSLATIONS = translate("update translations")
  global SWITCH_LANGUAGE
  SWITCH_LANGUAGE = translate("switch language")    
  global PLEASE_RESTART
  PLEASE_RESTART = translate("Please restart to see changes")
  global DEFAULT
  DEFAULT = translate("default")
  global USING
  USING = translate("using")
  global OK
  OK = translate("OK")
  global CANCEL
  CANCEL = translate("Cancel")  
setup_translations()

def update_language(locale: str) -> None:
  global use_languages
  use_languages = [locale]
  t = gettext.translation("apc", localedir=LOCALE_PATH, languages=use_languages)
  global translate
  translate = t.gettext
  setup_translations()

def _find_saves_path() -> str:
    steam_saves = Path().home() / "Documents/Avalanche Studios/COTW/Saves"
    steam_onedrive = Path().home() / "OneDrive/Documents/Avalanche Studios/COTW/Saves"
    epic_saves = Path().home() / "Documents/Avalanche Studios/Epic Games Store/COTW/Saves"
    epic_onedrive = Path().home() / "OneDrive/Documents/Avalanche Studios/Epic Games Store/COTW/Saves"
    
    base_saves = None
    if steam_saves.exists():
      base_saves = steam_saves
    elif epic_saves.exists():
      base_saves = epic_saves
    elif steam_onedrive.exists():
      base_saves = steam_onedrive
    elif epic_onedrive.exists():
      base_saves = epic_onedrive      

    save_folder = None
    if base_saves:
        folders = os.listdir(base_saves)
        all_numbers = re.compile(r"\d+")
        for folder in folders:
            if all_numbers.match(folder):
                save_folder = folder
                break
    if save_folder:
       return base_saves / save_folder
    else:
      return None

APP_DIR_PATH = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
DEFAULT_SAVE_PATH = _find_saves_path()
CONFIG_PATH = APP_DIR_PATH / "config"
SAVE_PATH = CONFIG_PATH / "save_path.txt"
SAVE_PATH.parent.mkdir(exist_ok=True, parents=True)
MOD_DIR_PATH = Path().cwd() / "mods"
MOD_DIR_PATH.mkdir(exist_ok=True, parents=True)
BACKUP_DIR_PATH = Path().cwd() / "backups"
BACKUP_DIR_PATH.mkdir(exist_ok=True, parents=True)
HIGH_NUMBER = 100000

ANIMAL_NAMES = json.load((CONFIG_PATH / "animal_names.json").open())["animal_names"]
RESERVE_NAMES = json.load((CONFIG_PATH / "reserve_names.json").open())["reserve_names"]
FUR_NAMES = json.load((CONFIG_PATH / "fur_names.json").open())["fur_names"]
RESERVES = json.load((CONFIG_PATH / "reserve_details.json").open())
ANIMALS = json.load((CONFIG_PATH / "animal_details.json").open())

class Reserve(str, Enum):
   hirsch = "hirsch"
   layton = "layton"
   medved = "medved"
   vurhonga = "vurhonga"
   parque = "parque"
   yukon = "yukon"
   cuatro = "cuatro"
   silver = "silver"
   teawaroa = "teawaroa"
   rancho = "rancho"
   mississippi = "mississippi"
   revontuli = "revontuli"
   newengland = "newengland"

class Strategy(str, Enum):
   go_all = "go-all"
   go_furs = "go-furs"
   go_some = "go-some"
   diamond_all = "diamond-all"
   diamond_furs = "diamond-furs"
   diamond_some = "diamond-some"
   males = "males"
   furs = "furs"
   furs_some = "furs-some"
   females = "females"

class GreatOnes(str, Enum):
   moose = "moose"
   black_bear = "black_bear"
   whitetail_deer = "whitetail_deer"
   red_deer = "red_deer"

class Levels(int, Enum):
  TRIVIAL = 1
  MINOR = 2
  VERY_EASY = 3
  EASY = 4
  MEDIUM = 5
  HARD = 6
  VERY_HARD = 7
  MYTHICAL = 8
  LEGENDARY = 9
  GREAT_ONE = 10
  
def get_level_name(level: Levels):
  if level == Levels.TRIVIAL:
   return translate("Trivial")
  if level == Levels.MINOR:
    return translate("Minor")
  if level == Levels.VERY_EASY:
    return translate("Very Easy")
  if level == Levels.EASY:
    return translate("Easy")
  if level == Levels.MEDIUM:
    return translate("Medium")
  if level == Levels.HARD:
    return translate("Hard")
  if level == Levels.VERY_HARD:
    return translate("Very Hard")
  if level == Levels.MYTHICAL:
    return translate("Mythical")
  if level == Levels.LEGENDARY:
    return translate("Legendary")
  if level == Levels.GREAT_ONE:
    return translate("Great One")
  return None

def format_key(key: str) -> str:
  key = [s.capitalize() for s in re.split("_|-", key)]
  return " ".join(key)

def load_config(config_path: Path) -> int: 
  config_path.read_text()

def get_save_path() -> Path:
  if SAVE_PATH.exists():
    return Path(SAVE_PATH.read_text())
  return DEFAULT_SAVE_PATH

def save_path(save_path_location: str) -> None:
  SAVE_PATH.write_text(save_path_location)

def get_reserve_species_renames(reserve_key: str) -> dict:
  reserve = get_reserve(reserve_key)
  return reserve["renames"] if "renames" in reserve else {}

def get_species_name(key: str) -> str:
  is_unique = species_unique_to_reserve(key)
  return F"{translate(ANIMAL_NAMES[key]['animal_name'])}{' ⋆' if is_unique else ''}"

def get_fur_name(key: str) -> str:
  return translate(FUR_NAMES[key]["fur_name"])

def species(reserve_key: str, include_keys = False) -> list:
   species_keys = RESERVES[reserve_key]["species"]
   return [f"{get_species_name(s)}{' (' + s + ')' if include_keys else ''}" for s in species_keys]

def get_species_key(species_name: str) -> str:
  for animal_name_key, names in ANIMAL_NAMES.items():
    if names["animal_name"] == species_name:
      return animal_name_key
  return None

def get_species_furs(species_key: str, gender: str) -> List[str]:
  species = get_species(species_key)
  if gender == "both":
    males = list(species["diamonds"]["furs"]["male"].values())
    females = list(species["diamonds"]["furs"]["female"].values())
    return males + females
  else:
    return list(species["diamonds"]["furs"][gender].values())

def get_reserve_species_name(species_key: str, reserve_key: str) -> str:
  renames = get_reserve_species_renames(reserve_key)
  species_key = renames[species_key] if species_key in renames else species_key
  return get_species_name(species_key)
  
def get_reserve_name(key: str) -> str:
  return translate(RESERVE_NAMES[key]["reserve_name"])

def reserve_keys() -> list:
  return list(dict.keys(RESERVES))

def reserves(include_keys = False) -> list:
   keys = list(dict.keys(RESERVES))
   return [f"{get_reserve_name(r)}{' (' + r + ')' if include_keys else ''}" for r in keys]  

def get_reserve(reserve_key: str) -> dict:
  return RESERVES[reserve_key]

def get_reserve_species(reserve_key: str) -> dict:
  return get_reserve(reserve_key)["species"]

def get_species(species_key: str) -> dict:
  return ANIMALS[species_key]

def get_diamond_gender(species_name: str) -> str:
  species_config = get_species(species_name)["diamonds"]
  return species_config["gender"] if "gender" in species_config else "male"  

def _get_fur(furs: dict, seed: int) -> str:
  try:
    return next(key for key, value in furs.items() if value == seed)
  except:
    return None

def get_animal_fur_by_seed(species: str, gender: str, seed: int) -> str:
  if species not in ANIMALS:
     return "-"

  animal = ANIMALS[species]
  go_furs = animal["go"]["furs"] if "go" in animal and "furs" in animal["go"] else []
  diamond_furs = animal["diamonds"]["furs"] if "furs" in animal["diamonds"] else []
  diamond_furs = diamond_furs[gender] if gender in diamond_furs else []
  go_key = _get_fur(go_furs, seed)
  diamond_key = _get_fur(diamond_furs, seed)
  if go_key:
    return get_fur_name(go_key)
  elif diamond_key:
    return get_fur_name(diamond_key)
  else:
    return "-"

def valid_species_for_reserve(species: str, reserve: str) -> bool:
  return reserve in RESERVES and species in RESERVES[reserve]["species"]

def valid_species(species: str) -> bool:
  return species in list(ANIMALS.keys())

def valid_go_species(species: str) -> bool:
    return species in GreatOnes.__members__

def valid_fur_species(species_key: str) -> bool:
  return True

def get_population_file_name(reserve: str):
    index = RESERVES[reserve]["index"]
    return f"animal_population_{index}"
  
def get_population_name(filename: str):
  for _reserve, details in RESERVES.items():
    reserve_filename = f"animal_population_{details['index']}"
    if reserve_filename == filename:
      return translate(details["name"])
  return None

def species_unique_to_reserve(species_key: str) -> bool:
  cnt = 0
  for _reserve_key, reserve_details in RESERVES.items():
    if species_key in reserve_details["species"]:
      cnt += 1
  return (cnt == 1)