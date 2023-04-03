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

def get_languages() -> list:
  supported_languages = ["en_US", "de_DE", "zh_CN", "ru_RU", "es_MX"]

  default_locale, _ = locale.getdefaultlocale()
  env_language = os.environ.get("LANGUAGE")
  if env_language:
    use_languages = env_language.split(':')
  else:
    use_languages = [default_locale]
  if "en_US" not in use_languages:
    use_languages.append("en_US")
  
  use_languages = list(filter(lambda x: x in supported_languages, use_languages))  
  return use_languages

LOCALE_PATH = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)) / "locale/"
use_languages = get_languages()
t = gettext.translation("apc", localedir=LOCALE_PATH, languages=["en_US"])
translate = t.gettext

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

APC = translate("Animal Population Changer")
SPECIES = translate("Species")
ANIMALS_TITLE = translate("Animals")
MALE = translate("Male")
MALES = translate("Males")
FEMALE = translate("Female")
FEMALES = translate("Females")
HIGH_WEIGHT = translate("High Weight")
HIGH_SCORE = translate("High Score")
LEVEL = translate("Level")
GENDER = translate("Gender")
WEIGHT = translate("Weight")
SCORE = translate("Score")
VISUALSEED = translate("Visual Seed")
FUR = translate("Fur")
DIAMOND = translate("Diamond")
GREATONE = translate("Great One")
SUMMARY = translate("Summary")
RESERVE = translate("Reserve")
RESERVES_TITLE = translate("Reserves")
RESERVE_NAME_KEY = translate("Reserve Name (key)")
YES = translate("Yes")
MODDED = translate("Modded")
SPECIES_NAME_KEY = translate("Species (key)")
VIEWING_MODDED = translate("viewing modded")
NEW_BUG = translate("Please copy and paste as a new bug on Nexusmods here")
ERROR = translate("Error")
UNEXPECTED_ERROR = translate("Unexpected Error")
WARNING = translate("Warning")
SAVED = translate("Saved")
DOES_NOT_EXIST = translate("does not exist")
FAILED_TO_BACKUP = translate("failed to backup game")
FAILED_TO_LOAD_BACKUP = translate("failed to load backup file")
FAILED_TO_LOAD_MOD = translate("failed to load mod")
FAILED_TO_UNLOAD_MOD = translate("failed to unload mod")
MOD_LOADED = translate("Mod has been loaded")
MOD_UNLOADED = translate("Mod has been unloaded")
VERSION = translate("Version")
HUNTING_RESERVE = translate("Hunting Reserve")
UPDATE_BY_PERCENTAGE = translate("update by percentage")
MORE_MALES = translate("More Males")
MORE_FEMALES = translate("More Females")
GREATONES = translate("Great Ones")
DIAMONDS = translate("Diamonds")
INCLUDE_RARE_FURS = translate("include rare furs")
ALL_FURS = translate("All Furs")
RESET = translate("Reset")
UPDATE_ANIMALS = translate("Update Animals")
JUST_FURS = translate("Just the Furs")
ONE_OF_EACH_FUR = translate("one of each fur")
OTHERS = translate("Others")
PARTY = translate("Party")
GREATONE_PARTY = translate("Great One Party")
DIAMOND_PARTY = translate("Diamond Party")
WE_ALL_PARTY = translate("We All Party")
FUR_PARTY = translate("Fur Party")
EXPLORE = translate("Explore")
DIAMONDS_AND_GREATONES = translate("diamonds and Great Ones")
LOOK_MODDED_ANIMALS = translate("look at modded animals")
LOOK_ALL_RESERVES = translate("look at all reserves")
ONLY_TOP_SCORES = translate("only top 10 scores")
SHOW_ANIMALS = translate("Show Animals")
FILES = translate("Files")
CONFIGURE_GAME_PATH = translate("Configure Game Path")
LIST_MODS = translate("List Mods")
LOAD_MOD = translate("Load Mod")
UNLOAD_MOD = translate("Unload Mod")
SELECT_FOLDER = translate("Select the folder where the game saves your files")
SAVES_PATH_TITLE = translate("Saves Path")
PATH_SAVED = translate("Game path saved")
CONFIRM_LOAD_MOD = translate("Are you sure you want to overwrite your game file with the modded one?")
BACKUP_WILL_BE_MADE = translate("Don't worry, a backup copy will be made.")
CONFIRMATION = translate("Confirmation")

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
  return translate(ANIMAL_NAMES[key]["animal_name"])

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

def get_animal_fur_by_seed(species: str, gender: str, seed: int) -> str: # TODO: translations?
  if species not in ANIMALS:
     return "-"

  animal = ANIMALS[species]
  go_furs = animal["go"]["furs"] if "go" in animal and "furs" in animal["go"] else []
  diamond_furs = animal["diamonds"]["furs"] if "furs" in animal["diamonds"] else []
  diamond_furs = diamond_furs[gender] if gender in diamond_furs else []
  go_key = _get_fur(go_furs, seed)
  diamond_key = _get_fur(diamond_furs, seed)
  if go_key:
    return format_key(go_key)
  elif diamond_key:
    return format_key(diamond_key)
  else:
    return "-"

def valid_species_for_reserve(species: str, reserve: str) -> bool:
  return reserve in RESERVES and species in RESERVES[reserve]["species"]

def valid_species(species: str) -> bool:
  return species in list(ANIMALS.keys())

def valid_go_species(species: str) -> bool:
    return species in GreatOnes.__members__

def valid_fur_species(species_key: str) -> bool:
  animal_species = ANIMALS[species_key]["diamonds"]
  gender = animal_species["gender"] if "gender" in animal_species else "male"
  return "furs" in animal_species and gender in animal_species["furs"]

def get_population_file_name(reserve: str):
    index = RESERVES[reserve]["index"]
    return f"animal_population_{index}"
  
def get_population_name(filename: str):
  for _reserve, details in RESERVES.items():
    reserve_filename = f"animal_population_{details['index']}"
    if reserve_filename == filename:
      return details["name"]
  return None