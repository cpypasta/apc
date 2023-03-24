import os
import re
import json
import sys
from pathlib import Path
from enum import Enum
from apc import __app_name__

def _find_saves_path() -> str:
    steam_saves = Path().home() / "Documents/Avalanche Studios/COTW/Saves"
    epic_saves = Path().home() / "Documents/Avalanche Studios/Epic Games Store/COTW/Saves"
    base_saves = None
    if steam_saves.exists():
      base_saves = steam_saves
    elif epic_saves.exists():
      base_saves = epic_saves

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
SAVE_PATH = APP_DIR_PATH / "config/save_path.txt"
ANIMAL_DETAILS_PATH = APP_DIR_PATH / "config/animal_details.json"
SAVE_PATH.parent.mkdir(exist_ok=True, parents=True)
MOD_DIR_PATH = Path().cwd() / "mods"
MOD_DIR_PATH.mkdir(exist_ok=True, parents=True)
HIGH_NUMBER = 100000

RESERVES = {
    "hirsch": {
        "name": "Hirschfelden",
        "index": 0,
        "species": [
          "wild_boar",
          "eu_rabbit",
          "fallow_deer",
          "eu_bison",
          "roe_deer",
          "red_fox",
          "pheasant",
          "canada_goose",
          "red_deer"
        ]
    },
    "layton": {
        "name": "Layton Lake",
        "index": 1,
        "species": [
          "moose",
          "jackrabbit",
          "mallard",
          "wild_turkey",
          "black_bear",
          "roosevelt_elk",
          "coyote",
          "blacktail_deer",
          "whitetail_deer"
        ]
    },
    "medved": {
        "name": "Medved-Taiga National Park",
        "index": 2,
        "species": [
          "musk_deer",
          "moose",
          "wild_boar",
          "reindeer",
          "eurasian_lynx",
          "brown_bear",
          "western_capercaillie",
          "gray_wolf"
        ]
    },
    "vurhonga": {
        "name": "Vurhonga Savanna",
        "index": 3,
        "species": [
          "eurasian_wigeon",
          "blue_wildebeest",
          "sidestriped_jackal",
          "gemsbok",
          "lesser_kudu",
          "scrub_hare",
          "lion",
          "warthog",
          "cape_buffalo",
          "springbok"
        ]
    },
    "parque": {
        "name": "Parque Fernando",
        "index": 4,
        "species": [
          "red_deer",
          "water_buffalo",
          "puma",
          "blackbuck",
          "cinnamon_teal",
          "collared_peccary",
          "mule_deer",
          "axis_deer"
        ]
    },
    "yukon": {
        "name": "Yukon Valley",
        "index": 6,
        "species": [
          "harlequin_duck",
          "moose",
          "red_fox",
          "caribou",
          "canada_goose",
          "grizzly_bear",
          "gray_wolf",
          "plains_bison"
        ]
    },
    "cuatro": {
        "name": "Cuatro Colinas Game Reserve",
        "index": 8,
        "species": [
          "southeastern_ibex",
          "ibearian_wolf",
          "red_deer",
          "iberian_mouflon",
          "wild_boar",
          "beceite_ibex",
          "eu_hare",
          "roe_deer",
          "ronda_ibex",
          "pheasant",
          "gredos_ibex"
        ]
    },
    "silver": {
        "name": "Sivler Ridge Peaks",
        "index": 9,
        "species": [
          "prong_horn",
          "puma",
          "mountain_goat",
          "bighorn_sheep",
          "wild_turkey",
          "black_bear",
          "mule_deer",
          "roosevelt_elk",
          "plains_bison"
        ]
    },
    "teawaroa": {
        "name": "Te Awaroa National Park",
        "index": 10,
        "species": [
          "red_deer",
          "eu_rabbit",
          "feral_pig",
          "fallow_deer",
          "chamois",
          "mallard",
          "wild_turkey",
          "sika_deer",
          "feral_goat"
        ]
    },
    "rancho": {
        "name": "Rancho del Arroyo",
        "index": 11,
        "species": [
          "mexican_bobcat",
          "rio_grande_turkey",
          "prong_horn",
          "bighorn_sheep",
          "collared_peccary",
          "antelope_jackrabbit",
          "mule_deer",
          "coyote",
          "pheasant",
          "whitetail_deer"
        ]        
    },
    "mississippi": {
        "name": "Mississippi Acres Preserve",
        "index": 12,
        "species": [
          "wild_hog",
          "raccoon",
          "eastern_cottontail_rabbit",
          "northern_bobwhite_quail",
          "eastern_wild_turkey",
          "gray_fox",
          "black_bear",
          "american_alligator",
          "green_wing_teal",
          "whitetail_deer"
        ]        
    },
    "revontuli": {
        "name": "Revontuli Coast",
        "index": 13,
        "species": [
          "mallard",
          "rock_ptarmigan",
          "eurasian_wigeon",
          "moose",
          "goldeneye",
          "puma",
          "tufted_duck",
          "black_grouse",
          "tundra_bean_goose",
          "willow_ptarmigan",
          "eu_lynx",
          "hazel_grouse",
          "eurasian_brown_bear",
          "eurasian_teal",
          "western_capercaillie",
          "raccoon_dog",
          "greylag_goose",
          "whitetail_deer",
          "canada_goose"
        ]        
    },
    "newengland": {
        "name": "New England Mountains",
        "index": 14,
        "species": [
          "mallard",
          "moose",
          "goldeneye",
          "raccoon",
          "rabbit",
          "bobwhite_quail",
          "turkey",
          "gray_fox",
          "red_fox",
          "black_bear",
          "bobcat",
          "coyote",
          "pheasant",
          "green_winged_teal",
          "whitetail_deer"
        ]        
    }
}

ANIMALS = json.load(ANIMAL_DETAILS_PATH.open())

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

class GreatOnes(str, Enum):
   moose = "moose"
   black_bear = "black_bear"
   whitetail_deer = "whitetail_deer"
   red_deer = "red_deer"

def load_config(config_path: Path) -> int: 
  config_path.read_text()

def get_save_path() -> Path:
  if SAVE_PATH.exists():
    return Path(SAVE_PATH.read_text())
  return DEFAULT_SAVE_PATH

def save_path(save_path_location: str) -> None:
  SAVE_PATH.write_text(save_path_location)

def get_reserve_name(key: str) -> str:
    return RESERVES[key]["name"]

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
    return go_key
  elif diamond_key:
    return diamond_key
  else:
    return "-"

def valid_go_species(species: str) -> bool:
    return species in GreatOnes.__members__