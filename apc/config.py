import os
import re
from pathlib import Path
from apc import __app_name__

def _find_saves_path() -> str:
    saves = Path().home() / "Documents/Avalanche Studios/COTW/Saves"
    save_folder = None
    if saves.exists():
        folders = os.listdir(saves)
        all_numbers = re.compile(r"\d+")
        for folder in folders:
            if all_numbers.match(folder):
                save_folder = folder
                break
    if save_folder:
       return saves / save_folder

def _parent_path() -> Path:
   return Path(os.path.realpath(__file__)).parents[0]

APP_DIR_PATH = _parent_path()
DEFAULT_SAVE_PATH = _find_saves_path()
SAVE_PATH = APP_DIR_PATH / "config/save_path.txt"
SAVE_PATH.parent.mkdir(exist_ok=True)
MOD_DIR_PATH = APP_DIR_PATH / "mods"
MOD_DIR_PATH.mkdir(exist_ok=True)

RESERVES = {
    "hirsch": {
        "name": "Hirschfelden",
        "index": 0,
        "species": [
          "wild_boar",
          "euro_rabbit",
          "fallow_deer",
          "euro_bison",
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
          "turkey",
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
          "w_capercaillie",
          "grey_wolf"
        ]
    },
    "vurhonga": {
        "name": "Vurhonga Savanna",
        "index": 3,
        "species": [
          "eu_wigeon",
          "blue_wildebeest",
          "s_striped_jackal",
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
          "cin_teal",
          "coll_peccary",
          "mule_deer",
          "axis_deer"
        ]
    },
    "yukon": {
        "name": "Yukon Valley",
        "index": 6,
        "species": [
          "h_duck",
          "moose",
          "red_fox",
          "caribou",
          "canada_goose",
          "grizzly_bear",
          "grey_wolf",
          "plains_bison"
        ]
    },
    "cuatro": {
        "name": "Cuatro Colinas Game Reserve",
        "index": 8,
        "species": [
          "ses_ibex",
          "ibearian_wolf",
          "red_deer",
          "iberian_mouflon",
          "wild_boar",
          "beceite_ibex",
          "european_hare",
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
          "pronghorn",
          "mountain_lion",
          "mountain_goat",
          "bighorn_sheep",
          "turkey",
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
          "euro_rabbit",
          "feral_pig",
          "fallow_deer",
          "chamois",
          "mallard",
          "turkey",
          "sika_deer",
          "feral_goat"
        ]
    },
    "rancho": {
        "name": "Rancho del Arroyo",
        "index": 11,
        "species": [
          "mexican_bobcat",
          "rg_turkey",
          "pronghorn",
          "bighorn_sheep",
          "coll_peccary",
          "ant_jackrabbit",
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
          "ect_rabbit",
          "bobwhite_quail",
          "ew_turkey",
          "gray_fox",
          "black_bear",
          "am_alligator",
          "gw_teal",
          "whitetail_deer"
        ]        
    },
    "revontuli": {
        "name": "Revontuli Coast",
        "index": 13,
        "species": [
          "mallard",
          "rock_ptarmigan",
          "eurasian_widgeon",
          "moose",
          "goldeneye",
          "mountain_lion",
          "tufted_duck",
          "black_grouse",
          "tbean_goose",
          "willow_ptarmigan",
          "eu_lynx",
          "hazel_grouse",
          "brown_bear",
          "eu_teal",
          "w_capercaillie",
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

ANIMALS = {
  "moose": {
    "go": {
      "score_low": 271,
      "score_high": 294,
      "weight_low": 605,
      "weight_high": 700,
      "furs": {
        "fabled_two_tone": 2834255352,
        "fabled_birch": 4184913762,
        "fabled_oak": 868192954,
        "fabled_speckled": 2725877565,
        "fabled_spruce": 2099598749,
        "fabled_ashen": 3430844549        
      }
    }
  },
  "red_deer": {
   "go": {
      "score_low": 239,
      "score_high": 279,
      "weight_low": 241,
      "weight_high": 260,
      "furs": {
        "fabled_spotted": 0
      }   
   }
  },
  "black_bear": {
   "go": {
      "score_low": 24,
      "score_high": 28,
      "weight_low": 291,
      "weight_high": 490,
      "furs": {
        "fabled_glacier": 2742609257,
        "fabled_chestnut": 3087602548,
        "fabled_cream": 3631307431,
        "fabled_spotted": 1868463965
      }   
   }
  },
  "whitetail_deer": {
   "go": {
      "score_low": 300,
      "score_high": 643,
      "weight_low": 97,
      "weight_high": 110,
      "furs": {
        "brown": 3758024868,
        "dark_brown": 3643313656,
        "tan": 203506860
      }   
   }
  }
}

GO_ALL_STRATEGY = "go-all"
GO_FURS_STRATEGY = "go-furs"
GO_SOME_STRATEGY = "go-some"

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