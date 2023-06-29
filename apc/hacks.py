import json, subprocess, pyautogui, time, re
from pathlib import Path
from apc import populations, adf, config, utils
from typing import List

def extract_animal_names(path: Path) -> dict:
  data = json.load(path.open())
  names = {}
  for animal in data.keys():
    names[animal] = { "animal_name": config.format_key(animal) }
  return {
    "animal_names": names
  }
  
def extract_reserve_names(path: Path) -> dict:
  data = json.load(path.open())
  names = {}
  for reserve in data.keys():
    names[reserve] = { "reserve_name": data[reserve]["name"] }
  return {
    "reserve_names": names
  }  

def extract_furs_names(path: Path) -> dict:
  data = json.load(path.open())
  fur_names = {}
  for animal in list(data.keys()):
    for _gender, furs in data[animal]["diamonds"]["furs"].items():
      for fur in furs.keys():        
        if fur not in fur_names:
          fur_name = config.format_key(fur)
          fur_names[fur] = { "fur_name": fur_name }
    if "go" in data[animal]:
      for fur in data[animal]["go"]["furs"].keys():
        if fur not in fur_names:
          fur_name = config.format_key(fur)
          fur_names[fur] = { "fur_name": fur_name }
  return {
    "fur_names": fur_names
  }

def bad_scores(path: Path) -> None:
  data = json.load(path.open())
  for animal_key in data.keys():
    animal = data[animal_key]
    if animal["diamonds"]["score_low"] > animal["diamonds"]["score_high"]:
      print(animal_key, animal)

def analyze_reserve(path: Path) -> None:
  pops = populations._get_populations(adf.load_adf(path, True).adf)
  group_weight = {}
  for p_i, p in enumerate(pops):
    groups = p.value["Groups"].value
    high_weight = 0
    for g in groups:
      animals = g.value["Animals"].value
      for a in animals:
        a = populations.AdfAnimal(a, "unknown")
        if a.weight > high_weight:
          high_weight = a.weight
    group_weight[p_i] = high_weight
  print(json.dumps(group_weight, indent=2))

FURS_PATH = Path("scans/furs.json")

class ApsAnimal:
  def __init__(self, animal_line: str) -> None:
    animal_parts = animal_line.split(",")
    self.species = utils.unformat_key(animal_parts[0])
    self.gender = "male" if animal_parts[2].lower() == "male" else "female"
    self.weight = float(animal_parts[3].split(" ")[0])
    self.score = float(animal_parts[4].split(" ")[0])
    self.score = float(animal_parts[4].split(" ")[0])
    self.fur = animal_parts[5].lower().rstrip()
  
  def __repr__(self) -> str:
    return f"{self.species}, {self.gender}, {self.weight}, {self.score}, {self.fur}"

def reset_ini() -> None:
  filename = Path("imgui.ini")
  content = filename.read_text()
  new_content = re.sub("Pos=\d+,\d+", "Pos=0,0", content, flags=re.RegexFlag.MULTILINE)
  filename.write_text(new_content)
  
def launch_aps() -> None:  
  reset_ini()
  subprocess.Popen(f"AnimalPopulationScanner.exe -p > scans\scan.csv", shell=True)  

def map_aps(reserve_name: str, species_key: str) -> str:
  if species_key == "eu_rabbit":
    return "euro_rabbit"
  if species_key == "eu_bison":
    return "euro_bison"
  if species_key == "siberian_musk_deer":
    return "musk_deer"
  if species_key == "eurasian_brown_bear":
    return "brown_bear"
  if species_key == "western_capercaillie":
    return "W.Capercaillie"
  if species_key == "gray_wolf":
    return "grey_wolf"
  if species_key == "eurasian_wigeon":
    return "Eu.Wigeon"
  if species_key == "sidestriped_jackal":
    return "S-Striped_jackal"
  if species_key == "cinnamon_teal":
    return "cin_teal"
  if species_key == "collared_peccary":
    return "coll._peccary"
  if species_key == "harlequin_duck":
    return "h_duck"
  if species_key == "gray_wolf":
    return "grey_wolf"
  if species_key == "eu_hare":
    return "european_hare"
  if species_key == "southeastern_ibex":
    return "ses_ibex"
  if species_key == "wild_turkey":
    return "turkey"
  if species_key == "prong_horn":
    return "pronghorn"
  if reserve_name == "silver" and species_key == "puma":
    return "mountain_lion"
  if species_key == "rockymountain_elk":
    return "rm_elk"
  if species_key == "rio_grande_turkey":
    return "rg_turkey"
  if species_key == "antelope_jackrabbit":
    return "ant._jackrabbit"
  if species_key == "northern_bobwhite_quail":
    return "Bobwhite_Quail"
  if species_key == "green_wing_teal":
    return "green-winged_teal"
  if species_key == "eastern_cottontail_rabbit":
    return "ect_rabbit"
  if species_key == "eastern_wild_turkey":
    return "ew_turkey"
  if reserve_name == "mississippi" and species_key == "feral_pig":
    return "wild_hog"
  if species_key == "american_alligator":
    return "Am._Alligator"
  if species_key == "tundra_bean_goose":
    return "t.bean_goose"
  if species_key == "eurasian_teal":
    return "eu.teal"
  
  return species_key

"""
Captures first seed that gives fur
"""
def process_aps(species_key: str, filename: Path) -> None:
  scanned_furs = {}
  with filename.open() as csvfile:
    animals = csvfile.readlines()
    for animal in animals:
      try:
        animal = ApsAnimal(animal)        
        if animal.species.lower() == species_key.lower():
          if animal.gender not in scanned_furs:
            scanned_furs[animal.gender] = {}
          if animal.fur not in scanned_furs[animal.gender]:
            scanned_furs[animal.gender][animal.fur] = animal.weight
      except:
        pass
  return scanned_furs

def combine_furs(existing: dict, latest: dict) -> None:
  existing_female_furs = existing["female"] if "female" in existing else {}
  latest_female_furs = latest["female"] if "female" in latest else {}
  existing_male_furs = existing["male"] if "male" in existing else {}
  latest_male_furs = latest["male"] if "male" in latest else {}
    
  for fur, seed in latest_female_furs.items():
    fur = fur.replace(" ", "_")
    if fur not in existing_female_furs and seed != 0.0:
      existing_female_furs[fur] = int(seed)
  for fur, seed in latest_male_furs.items():
    fur = fur.replace(" ", "_")
    if fur not in existing_male_furs and seed != 0.0:
      existing_male_furs[fur] = int(seed)
      
  new_existing = {
    "male": existing_male_furs,
    "female": existing_female_furs
  }
  return new_existing

def combine_furs2(existing: dict, latest: dict, gender: str, last_seed: float, new_seed: float) -> None:
  existing_furs = existing[gender] if gender in existing else {}
  latest_furs = latest[gender] if gender in latest else {}
  print(existing_furs)
  print(latest_furs)
    
  for fur, seed in latest_furs.items():
    seed = int(seed)
    if fur not in existing_furs:
      existing_furs[fur] = range(last_seed, new_seed)
    else:
      existing_fur = existing_furs[fur]
      if existing_fur.stop == last_seed:
        existing_fur = range(existing_fur.start, seed)
      else:
        existing_furs[f'{fur}2'] = range(last_seed, new_seed)
      
  new_existing = {
    "male": existing_furs if gender == "male" else existing["male"],
    "female": existing_furs if gender == "female" else existing["female"]
  }
  return new_existing

def show_mouse() -> None:
  try:
      while True:
          x, y = pyautogui.position()
          positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
          print(positionStr, end='')
          print('\b' * len(positionStr), end='', flush=True)
  except KeyboardInterrupt:
      print('\n')  

def click() -> None:
  pyautogui.mouseDown()
  time.sleep(0.2)
  pyautogui.mouseUp()

def doubleClick() -> None:
  pyautogui.mouseDown()
  pyautogui.mouseUp()
  pyautogui.mouseDown()
  pyautogui.mouseUp()  

def click_reserve(reserve_name: str) -> None:
  pyautogui.moveTo(500, 174, duration=0.5)
  click()
  if reserve_name == "hirsch":
    pyautogui.moveTo(500, 195, duration=0.2)
    click()
  if reserve_name == "layton":
    pyautogui.moveTo(500, 215, duration=0.2)
    click()
  if reserve_name == "medved":
    pyautogui.moveTo(500, 235, duration=0.2)
    click()
  if reserve_name == "vurhonga":
    pyautogui.moveTo(500, 255, duration=0.2)
    click()      
  if reserve_name == "parque":
    pyautogui.moveTo(500, 265, duration=0.2)
    click()      
  if reserve_name == "yukon":
    pyautogui.moveTo(500, 285, duration=0.2)
    click()       
  if reserve_name == "cuatro":
    pyautogui.moveTo(500, 295, duration=0.2)
    click()       
  if reserve_name == "silver":
    pyautogui.moveTo(500, 310, duration=0.2)
    click()         
  if reserve_name == "teawaroa":
    pyautogui.moveTo(512, 228, duration=0.2)
    pyautogui.dragTo(512, 282, duration=0.5)
    pyautogui.moveTo(403, 247)
    click()         
  if reserve_name == "rancho":
    pyautogui.moveTo(512, 228, duration=0.2)
    pyautogui.dragTo(512, 282, duration=0.5)
    pyautogui.moveTo(403, 270)
    click()         
  if reserve_name == "mississippi":
    pyautogui.moveTo(512, 228, duration=0.2)
    pyautogui.dragTo(512, 282, duration=0.5)
    pyautogui.moveTo(403, 286)
    click()         
  if reserve_name == "revontuli":
    pyautogui.moveTo(512, 228, duration=0.2)
    pyautogui.dragTo(512, 282, duration=0.5)
    pyautogui.moveTo(403, 305)
    click()         
  if reserve_name == "newengland":
    pyautogui.moveTo(512, 228, duration=0.2)
    pyautogui.dragTo(512, 282, duration=0.5)
    pyautogui.moveTo(403, 318)
    click() 
  if reserve_name == "emerald":
    pyautogui.moveTo(512, 228, duration=0.2)
    pyautogui.dragTo(512, 292, duration=0.5)
    pyautogui.moveTo(403, 325)
    click()     
    
  pyautogui.moveTo(500, 275, duration=0.2)
  doubleClick()    
  pyautogui.moveTo(1469, 116, duration=0.5)
  click()
      
def load_furs() -> dict:
  return json.load(FURS_PATH.open())      
      
def save_furs(furs: dict) -> None:
  FURS_PATH.write_text(json.dumps(furs, indent=2))      
      
def seed_animals(reserve_key: str) -> None:  
  print()
  print(config.get_reserve_name(reserve_key))
  print()
  reserve_species = config.get_reserve(reserve_key)["species"]
  all_furs = load_furs()
  for species in reserve_species:
    aps_species = map_aps(reserve_key, species)
    print(species.upper())
    if species in all_furs:
      print(f"{aps_species} already processed")
      continue    
    reserve = adf.load_reserve(reserve_key, False, False)    
    species_details = populations._species(reserve_key, reserve.adf, species)
    groups = species_details.value["Groups"].value  
    species_furs = {}    
    for gender in [1, 2]:
      seed = 0
      while seed < 12000:
        initial_seed = seed
        seed = populations.diamond_test_seed(species, groups, reserve.decompressed.data, seed, gender)
        print(f"[{initial_seed}-{seed}]")
        reserve.decompressed.save(config.MOD_DIR_PATH, False)
        launch_aps()
        click_reserve(reserve_key)
        new_furs = process_aps(aps_species, Path(f"scans/scan.csv"))
        if not bool(new_furs):
          print(f"we didn't find any furs; probably have name wrong: {species.lower()}:{utils.unformat_key(aps_species).lower()}")
          seed = initial_seed
          continue
        species_furs = combine_furs(species_furs, new_furs)
        print(species_furs)
        
    if bool(species_furs):
      print(species_furs)
      all_furs[species] = species_furs
      save_furs(all_furs)

"""
{
  "fallow_deer": {
    "male": {
      "piebald": range(0, 20), 0-19 inclusive
      "brown": range(20, 40)
    }
  }
}
"""

def seed_animals2(reserve_key: str, species: str) -> None:  
  print()
  print(config.get_reserve_name(reserve_key))
  print()
  aps_species = map_aps(reserve_key, species)
  print(species.upper())   
  reserve = adf.load_reserve(reserve_key, False, False)    
  species_details = populations._species(reserve_key, reserve.adf, species)
  groups = species_details.value["Groups"].value  
  species_furs = { "male": {}, "female": {} }    
  for gender in [1, 2]:
    seed = 0
    while seed < 12000:
      initial_seed = seed
      seed = populations.diamond_test_seed(species, groups, reserve.decompressed.data, seed, gender)
      print(f"[{initial_seed}-{seed}]")
      reserve.decompressed.save(config.MOD_DIR_PATH, False)
      launch_aps()
      click_reserve(reserve_key)
      new_furs = process_aps(aps_species, Path(f"scans/scan.csv"))
      species_furs = combine_furs2(species_furs, new_furs, "male" if gender == 1 else "female", initial_seed, seed)  
      print(species_furs)
      print()    
  print(json.dumps(species_furs, indent=2))

def get_reserve_keys() -> list:
  return list(dict.keys(config.RESERVES))

def test_reserve(reserve_key) -> None:
  print(reserve_key)
  launch_aps()
  click_reserve(reserve_key)  

def seed_reserves() -> None:
  reserves_keys = get_reserve_keys()
  for reserve in reserves_keys:
    seed_animals(reserve)

def verify_seeds(seeds: List[int]) -> None:
  reserve_name = "cuatro"
  species = "beceite_ibex" 
  reserve = adf.load_reserve(reserve_name, False, False)
  species_details = populations._species(reserve_name, reserve.adf, species)
  groups = species_details.value["Groups"].value
  populations.diamond_test_seeds(species, groups, reserve.decompressed.data, seeds)
  reserve.decompressed.save(config.MOD_DIR_PATH, False)
  print("done")

def calc_seed(furs: List[int]) -> None:
  total = sum(furs)
  per = [fur / total for fur in furs]
  for i in range(0, 100000):
    block = 100 + i    
    fur_size = [round(block * fur) for fur in per]
    current = 0
    blocks = []
    for i, size in enumerate(fur_size):    
      if i == 0:
        blocks.append((current, current+size))
        current += size + 1
      else:
        blocks.append((current, size + blocks[i-1][1]))
        current += size
    if blocks[1][0] == 2497 and blocks[1][1] == 2506:
      print(block)    
      print(blocks)

def convert_fur_float_to_int(furs: dict) -> dict:
  for fur in furs["male"]:
    furs["male"][fur] = int(furs["male"][fur])
  for fur in furs["female"]:
    furs["female"][fur] = int(furs["female"][fur])
  return furs    

def merge_furs_into_animals() -> None:
  animals = json.load(Path("apc/config/animal_details.json").open())
  furs = load_furs()
  
  for animal_name, animal in animals.items():
    animal_furs = convert_fur_float_to_int(furs[animal_name])
    animal["diamonds"]["furs"] = animal_furs
  Path("apc/config/animal_details.json").write_text(json.dumps(animals, indent=2))

def fix_furs() -> None:
  animals = json.load(Path("apc/config/animal_details.json").open())
  for _, animal in animals.items():
    if isinstance(list(animal["diamonds"]["furs"]["male"].values())[0], float):
      animal["diamonds"]["furs"] = convert_fur_float_to_int(animal["diamonds"]["furs"])
  Path("apc/config/animal_details.json").write_text(json.dumps(animals, indent=2))
      
if __name__ == "__main__":
  # analyze_reserve(config.get_save_path() / "animal_population_16")
  # fix_furs()
  seed_animals("newengland")
  # launch_aps()
  # click_reserve("emerald")