import PySimpleGUI as sg
import sys, traceback, time, os, re, shutil, subprocess, textwrap
from apc import populations, adf, config
from apc.config import valid_go_species, Strategy, MOD_DIR_PATH, save_path, get_save_path, get_population_file_name, get_population_name, BACKUP_DIR_PATH, valid_fur_species, format_key, get_reserve_species, get_diamond_gender, get_species_name
from apcgui import __version__, logo, config
from typing import List
from pathlib import Path

DEFAULT_FONT = "_ 14"
MEDIUM_FONT = "_ 13"
BUTTON_FONT = "_ 13"
SMALL_FONT = "_ 11"
PROGRESS_DELAY = 0.3
VIEW_MODDED=None
VIEW_MOD_LOADED=None

RESERVE_COLUMNS = None
SPECIES_COLUMNS = None

reserve_keys = config.reserve_keys()
reserve_names = None
reserve_name_size = None
save_path_value = get_save_path()
reserve_description = None
species_group_details = None
male_group_cnt = None
female_group_cnt = None
symbol_closed = "►"
symbol_open = "▼"

class Animal:
  def __init__(self, gender: str, weight: float, score: float, fur: str, go: bool, diamond_gender: str) -> None:
    self.gender = gender
    self.weight = weight
    self.score = score
    self.fur = fur if fur != "" else None
    self.go = go
    self.diamond_gender = diamond_gender
    self.gender_key = "male" if gender == config.MALE else "female"
    self.can_be_diamond = self.gender_key == diamond_gender or diamond_gender == "both"
    
  def fur_key(self, species_key: str):
    if self.fur == None:
      return None
    fur_names, fur_keys = config.get_species_fur_names(species_key, self.gender_key, self.go)
    print("Name:", self.fur, "Index:", fur_names.index(self.fur), "Key:", fur_keys[fur_names.index(self.fur)])
    return fur_keys[fur_names.index(self.fur)]
  
  def __repr__(self) -> str:
    return f"{self.gender_key}, {self.weight}, {self.score}, {self.fur}, {self.go}"

def _progress(window: sg.Window, value: int) -> None:
 window["progress"].update(value)   

def _show_error_window(error):
  layout = [
    [sg.T(f"{config.NEW_BUG}:")],
    [sg.Multiline("https://www.nexusmods.com/thehuntercallofthewild/mods/225?tab=bugs", expand_x=True, no_scrollbar=True, disabled=True)],
    [sg.T(f"{config.ERROR}:")],
    [sg.Multiline(error, expand_x=True, expand_y=True, disabled=True)]
  ]
  window = sg.Window(config.UNEXPECTED_ERROR, layout, modal=True, size=(600, 300), icon=logo.value)
  while True:
    event, _values = window.read()
    if event == sg.WIN_CLOSED:
      break 

def _show_popup(message: str, title: str, ok: str, cancel: str = None) -> str:
  buttons = [sg.Button(ok, k="ok", font=DEFAULT_FONT)]
  if cancel:
    buttons.append(sg.Button(cancel, k="cancel", font=DEFAULT_FONT))
  
  layout = [
    [sg.T(message, font=DEFAULT_FONT, p=(0,10))],
    [sg.Push(), buttons]
  ]
  window = sg.Window(title, layout, modal=True, icon=logo.value)
  response = None
  while True:
    event, _values = window.read()
    if event == sg.WIN_CLOSED:
      response = "cancel"
      break
    if event == "ok":
      response = "ok"
      break
    elif event == "cancel":
      response = "cancel"
      break
  window.close()
  return response

def _show_export_popup(reserve: str, file: Path) -> str: 
  default_path = config.EXPORTS_PATH / file
  layout = [
    [sg.T(f"{config.EXPORT_MSG}:", font=DEFAULT_FONT, p=(0,10))],
    [sg.FileSaveAs(f"{config.EXPORT_AS}...", initial_folder=config.EXPORTS_PATH, font=DEFAULT_FONT, target="export_path", k="export_btn", enable_events=True, change_submits=True), sg.T(default_path, k="export_path")],
    [sg.Push(), sg.Button(config.CANCEL, k="cancel", font=DEFAULT_FONT), sg.Button(config.EXPORT, k="export", font=DEFAULT_FONT)]
  ]
  window = sg.Window(f"{config.EXPORT_MOD}: {reserve}", layout, modal=True, icon=logo.value)
  response = None
  while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
      response = "cancel"
      break
    if event == "export":
      response = values["export_btn"] if values["export_btn"] != '' else default_path
      break
    elif event == "cancel":
      response = "cancel"
      break
  window.close()
  return response

def _show_import_popup(reserve: str, file: str) -> str: 
  layout = [
    [sg.T(f"{config.IMPORT_MSG}:", font=DEFAULT_FONT, p=(0,10))],
    [sg.FileBrowse(config.SELECT_FILE, initial_folder=config.EXPORTS_PATH, font=DEFAULT_FONT, target="import_path", k="import_btn"), sg.T(file, k="import_path")],
    [sg.Push(), sg.Button(config.CANCEL, k="cancel", font=DEFAULT_FONT), sg.Button(config.IMPORT, k="import", font=DEFAULT_FONT)]
  ]
  window = sg.Window(f"{config.IMPORT_MOD}: {reserve}", layout, modal=True, icon=logo.value)
  response = None
  while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
      response = "cancel"
      break
    if event == "import":
      response = values["import_btn"]
      break
    elif event == "cancel":
      response = "cancel"
      break
  window.close()
  return response

def _highlight_values(data: list) -> list:
  diamond_index = 6
  go_index = 7
  for row in data:
    if row[diamond_index] > 0:
      row[diamond_index] = f"* {row[diamond_index]}"
    else:
      row[diamond_index] = str(row[diamond_index])
    if row[go_index] > 0:
      row[go_index] = f"** {row[go_index]}"
    else:
      row[go_index] = str(row[go_index])      
  return data

def _disable_diamonds(window: sg.Window, disabled: bool) -> None:
  window["diamond_value"].update(disabled = disabled)
  window["gender_value"].update(disabled = disabled)

def _disable_furs(window: sg.Window, disabled: bool) -> None:
  window["fur_update_animals"].update(disabled = disabled)

def _disable_go(window: sg.Window, disabled: bool) -> None:
  window["go_value"].update(disabled = disabled)

def _disable_new_reserve(window: sg.Window) -> None:
  _disable_diamonds(window, True)
  _disable_furs(window, True)
  _disable_go(window, True)  
  window["show_animals"].update(disabled=True)
  window["update_animals"].update(disabled=True)

def _disable_animal_details(window: sg.Window, disabled: bool) -> None:
  window["animal_go"].update(disabled=disabled)
  window["animal_gender"].update(disabled=disabled)
  window["animal_fur"].update(disabled=disabled)  
  window["update_animal"].update(disabled=disabled) 

def _get_go_species(reserve_key: str) -> List[str]:
  species = get_reserve_species(reserve_key)
  found = []
  for animal in species:
    if valid_go_species(animal):
      found.append(animal)
  return found 

def _disable_go_parties(window: sg.Window, reserve_key: str) -> None:
  found = len(_get_go_species(reserve_key)) > 0
  window["go_party"].update(disabled=(not found))
    
def _reserve_key_from_name(name: str) -> str:
  return reserve_keys[reserve_names.index(name)]

def _show_species_description(window: sg.Window, reserve_key: str, species_name: str, is_modded: bool, is_top: bool) -> None:
  is_loaded_mod = _is_reserve_mod_loaded(reserve_key, window)
  window["reserve_description"].update(visible=False)
  window["modding"].update(visible=False)
  window["species_description"].update(visible=True)
  window["show_reserve"].update(visible=True)
  window["exploring"].update(visible=True)
  window["species_name"].update(f"{species_name.upper()}{f' ({config.MODDED})' if is_modded else ''} {f'({config.LOADED_MOD})' if is_loaded_mod else ''} {f'({config.TOP_10})' if is_top else ''}")
  window["mod_list"].update(visible=False)

def _show_reserve_description(window: sg.Window) -> None:
    window["reserve_description"].update(visible=True)
    window["modding"].update(visible=True)
    window["species_description"].update(visible=False)
    window["show_reserve"].update(visible=False)
    window["exploring"].update(visible=False)
    window["species_name"].update("")
    window['reserve_warning'].update(visible=True)   
    window["mod_list"].update(visible=False) 
    window["mod_tab"].update(disabled=False)
    window["mod_tab"].select()
    window["fur_tab"].update(disabled=False)    
    window["explore_tab"].update(disabled=False)    
    window["party_tab"].update(disabled=False)
    window["reserve_note"].update("")
    window["load_mod"].update(disabled=True)
    window["unload_mod"].update(disabled=True)    
    window["export_mod"].update(disabled=True)
    window["import_mod"].update(disabled=True)    
    _clear_animal_details(window)
    _disable_animal_details(window, True)

def _show_mod_list(window: sg.Window) -> None:
  window["reserve_description"].update(visible=False)
  window["mod_list"].update(visible=True)
  window["show_reserve"].update(visible=True)
  window["mod_tab"].update(disabled=True)
  window["fur_tab"].update(disabled=True)
  window["explore_tab"].update(disabled=True)
  window["party_tab"].update(disabled=True)
  window["load_mod"].update(disabled=True)
  window["unload_mod"].update(disabled=True)
  window["export_mod"].update(disabled=True)
  window["import_mod"].update(disabled=True)
  
def _viewing_modded(window: sg.Window) -> bool:
  return window['reserve_warning'].get() == VIEW_MODDED  

def _is_diamond_enabled(window: sg.Window, value: int) -> bool:
  return value != 0

def _is_go_enabled(window: sg.Window, value: int) -> bool:
  return not window["go_value"].Disabled and value != 0

def _show_error(window: sg.Window, ex: adf.FileNotFound) -> None:
  window["progress"].update(0)      
  window["reserve_note"].update(f"{config.ERROR}: {ex}")      
  print("ERROR", traceback.print_exc(file=sys.stdout))   
   
def _show_warning(window: sg.Window, message: str) -> None:
  window["progress"].update(0)      
  window["reserve_note"].update(f"{config.WARNING}: {message}")

def _clear_furs(window: sg.Window) -> None:
  window["male_furs"].update([])
  window["female_furs"].update([])  
  window["diamond_furs"].update(values=[])
  window["diamond_gender"].update("")

def _mod_furs(window: sg.Window, reserve_key: str, species_key: str, male_fur_keys: List[str], female_fur_keys: List[str], male_fur_cnt: int, female_fur_cnt: int):
  print((reserve_key, species_key, "furs", male_fur_keys, male_fur_cnt, female_fur_keys, female_fur_cnt))
  is_modded = _viewing_modded(window)
  try:
    reserve_details = adf.load_reserve(reserve_key, mod=is_modded)
  except Exception as ex:
    _show_error(window, ex)
    return
  window["progress"].update(25)
  try:
   populations.mod_furs(reserve_key, reserve_details, species_key, male_fur_keys, female_fur_keys, male_fur_cnt, female_fur_cnt)
  except Exception as ex:    
    _show_error(window, ex)
    return
  window["progress"].update(75)
  window["reserve_warning"].update(VIEW_MODDED)
  window["fur_update_animals"].update(disabled = True)
  window["show_animals"].update(disabled=True)
  window["update_animals"].update(disabled=True)  
  window["modded_reserves"].update(True)  
  window["reserve_note"].update(f"{get_species_name(species_key).upper()} (Update Furs) {config.SAVED}: \"{MOD_DIR_PATH / get_population_file_name(reserve_key)}\"")
  window["reserve_description"].update(select_rows = [])
  window["progress"].update(100)
  time.sleep(PROGRESS_DELAY)
  window["progress"].update(0)
  _reset_furs(window)
  _clear_furs(window)

def _mod_diamonds(window: sg.Window, reserve_key: str, species_key: str, diamond_cnt: int, male_fur_keys: List[str], female_fur_keys: List[str]) -> None:
  print((reserve_key, species_key, "diamonds", diamond_cnt, male_fur_keys, female_fur_keys))
  global reserve_description
  is_modded = _viewing_modded(window)
  try:
    reserve_details = adf.load_reserve(reserve_key, mod=is_modded)
  except Exception as ex:
    _show_error(window, ex)
    return
  window["progress"].update(25)
  try:
    reserve_description, _ = populations.mod_diamonds(reserve_key, reserve_details, species_key, diamond_cnt, male_fur_keys, female_fur_keys)
  except Exception as ex:    
    _show_error(window, ex)
    return
  window["progress"].update(50)
  window["reserve_description"].update(_highlight_values(_format_reserve_description(reserve_description)))
  window["progress"].update(75)
  window["reserve_warning"].update(VIEW_MODDED)
  window["reserve_note"].update(f"{get_species_name(species_key).upper()} (Diamonds) {config.SAVED}: \"{MOD_DIR_PATH / get_population_file_name(reserve_key)}\"")
  window["progress"].update(100)
  time.sleep(PROGRESS_DELAY)
  window["progress"].update(0)  
  window["show_animals"].update(disabled=True)
  window["update_animals"].update(disabled=True)
  window["modded_reserves"].update(True)
  window["fur_update_animals"].update(disabled = True)

def _mod_animal(window: sg.Window, reserve_key: str, species_key: str, animal: Animal, adfAnimal: populations.AdfAnimal) -> None:
  print((reserve_key, species_key, "mod animal"))
  global reserve_description
  is_modded = _viewing_modded(window)
  try:
    reserve_details = adf.load_reserve(reserve_key, mod=is_modded)
  except Exception as ex:
    _show_error(window, ex)
    return
  window["progress"].update(25)
  try:
    populations.mod_animal(reserve_details, species_key, adfAnimal, animal.go, animal.gender_key, animal.weight, animal.score, animal.fur_key(species_key))
  except Exception as ex:    
    _show_error(window, ex)
    return
  window["progress"].update(50)
  window["progress"].update(75)
  window["reserve_warning"].update(VIEW_MODDED)
  window["reserve_note"].update(f"{get_species_name(species_key).upper()} (Animal Update) {config.SAVED}: \"{MOD_DIR_PATH / get_population_file_name(reserve_key)}\"")
  window["progress"].update(100)
  time.sleep(PROGRESS_DELAY)
  window["progress"].update(0)  
  _clear_animal_details(window)  
  _disable_animal_details(window, True)
  window["species_description"].update(select_rows=[])

def _mod(reserve_key: str, species: str, strategy: Strategy, window: sg.Window, modifier: int, rares: bool, percentage: bool = False) -> None:
  print((reserve_key, species, strategy.value, modifier, rares))
  global reserve_description
  is_modded = _viewing_modded(window)
  try:
    reserve_details = adf.load_reserve(reserve_key, mod=is_modded)
  except Exception as ex:
    _show_error(window, ex)
    return
  window["progress"].update(25)
  try:
    reserve_description, _ = populations.mod(reserve_key, reserve_details, species, strategy.value, rares=rares, modifier=modifier, percentage=percentage)
  except Exception as ex:    
    _show_error(window, ex)
    return
  window["progress"].update(50)
  window["reserve_description"].update(_highlight_values(_format_reserve_description(reserve_description)))
  window["progress"].update(75)
  window["reserve_warning"].update(VIEW_MODDED)
  window["reserve_note"].update(f"{get_species_name(species).upper()} ({format_key(strategy)}) {config.SAVED}: \"{MOD_DIR_PATH / get_population_file_name(reserve_key)}\"")
  window["progress"].update(100)
  time.sleep(PROGRESS_DELAY)
  window["progress"].update(0)  
  window["show_animals"].update(disabled=True)
  window["update_animals"].update(disabled=True)
  window["modded_reserves"].update(True)
  window["fur_update_animals"].update(disabled = True)

def _list_mods(window: sg.Window) -> List[List[str]]:
  if not MOD_DIR_PATH.exists():
    return _show_warning(window, f"{MOD_DIR_PATH} {config.DOES_NOT_EXIST}.")
  
  file_format = re.compile(r"^.*animal_population_\d+$")
  items = os.scandir(MOD_DIR_PATH)
  mods = []
  for item in items:
    item_path = MOD_DIR_PATH / item.name
    if item.is_file() and file_format.match(item.name):
      already_loaded = (BACKUP_DIR_PATH / item.name).exists()
      already_loaded_name = config.YES if already_loaded else "-"
      mods.append([get_population_name(item.name), already_loaded_name, item_path, item.name, already_loaded])
  return mods

def _is_reserve_mod_loaded(reserve_key: str, window: sg.Window) -> bool:
  mods = _list_mods(window)
  for mod in mods:
    if config.get_population_reserve_key(mod[3]) == reserve_key:      
      return mod[4]

def _copy_file(filename: Path, destination: Path) -> None:
  print("copy", filename, "to", destination)
  return shutil.copy2(filename, destination)

def _backup_exists(filename: Path) -> bool:
  return (BACKUP_DIR_PATH / filename.name).exists()

def _load_mod(window: sg.Window, filename: Path) -> None:
  window["reserve_note"].update("")
  try:
    if not _backup_exists(filename):
      game_file = get_save_path() / filename.name
      if game_file.exists():
        backup_path = _copy_file(game_file, BACKUP_DIR_PATH)
        if not backup_path:
          _show_warning(window, f"{config.FAILED_TO_BACKUP} {game_file}")
          return
    else:
      print("backup already exists")
    _progress(window, 50)
    game_path = _copy_file(filename, get_save_path())
    if not game_path:
      _show_warning(window, f"{config.FAILED_TO_LOAD_MOD} {filename}")
      return    
    _progress(window, 100)
    sg.PopupQuickMessage(config.MOD_LOADED, font="_ 28", background_color="brown")
    time.sleep(PROGRESS_DELAY)
  except Exception:
    print(traceback.format_exc())
    _show_warning(window, {config.FAILED_TO_LOAD_MOD})    
  _progress(window, 0)

def _unload_mod(window: sg.Window, filename: Path) -> None:
  window["reserve_note"].update("")
  try:
    backup_file = BACKUP_DIR_PATH / filename.name
    game_path = get_save_path()
    if not backup_file.exists():
      _show_warning(window, f"{backup_file} {config.DOES_NOT_EXIST}")
      return
    game_path = _copy_file(backup_file, game_path)    
    if not game_path:
      _show_warning(window, f"{config.FAILED_TO_LOAD_BACKUP} {game_path}")
      return
    _progress(window, 50)
    os.remove(backup_file)
    _progress(window, 100)
    sg.PopupQuickMessage(config.MOD_UNLOADED, font="_ 28", background_color="brown")
    time.sleep(PROGRESS_DELAY)
  except Exception:
    print(traceback.format_exc())
    _show_warning(window, f"{config.FAILED_TO_UNLOAD_MOD}")    
  _progress(window, 0)

def _process_list_mods(window: sg.Window, reserve_name: str = None) -> list:
  window["reserve_note"].update("")
  _show_mod_list(window)
  window["progress"].update(30)
  mods = _list_mods(window)
  window["progress"].update(60)
  window["mod_list"].update(mods)
  if reserve_name:
    for mod_i, mod in enumerate(mods):
      if mod[0] == reserve_name:
        window["mod_list"].update(select_rows=[mod_i])
  window["progress"].update(100)
  time.sleep(PROGRESS_DELAY)
  window["progress"].update(0)
  return mods 

def _format_reserve_description(reserve_description: List) -> List:
  rows = []
  for row in reserve_description:
    rows.append(row[2:])
  return rows

def _reset_mod(window: sg.Window) -> None:
  window["gender_value"].update(0, range=(0,0))
  window["go_value"].update(0)
  window["diamond_value"].update(0)
  window["diamond_all_furs"].update(False)
  window["diamond_furs"].update(set_to_index=[])
  window["reserve_description"].update(select_rows=[])

def _reset_furs(window: sg.Window) -> None:
  window["male_all_furs"].update(False)
  window["female_all_furs"].update(False)
  window["male_furs"].update(set_to_index=[])
  window["female_furs"].update(set_to_index=[])
  window["male_fur_animals_cnt"].update(0)  
  window["female_fur_animals_cnt"].update(0)  

def _clear_animal_details(window: sg.Window) -> None:
  window["animal_go"].update([])
  window["animal_gender"].update([])
  window["animal_weight"].update(0, range=(0,0))
  window["animal_score"].update(0, range=(0,0))
  window["animal_fur"].update(values=[])
  window["animal_weight_info"].update("")
  window["animal_score_info"].update("")

def _update_mod_animal_counts(window: sg.Window, species: str, total_cnt: int, org_male_cnt: int, org_female_cnt: int, female_cnt: int, male_cnt: int, go_cnt: int, diamond_cnt: int, male_group_cnt: int, female_group_cnt: int, changing: str = None) -> None:  
  # print("C:", changing, "M:", male_cnt, "F:", female_cnt, "D:", diamond_cnt, "G:", go_cnt)
  window["new_female_value"].update(female_cnt)
  window["new_male_value"].update(male_cnt)
  if changing == None:
    window["gender_value"].update(value=0, range=(-male_cnt, female_cnt))
  if changing in ("male", "female") or changing == None:
    if valid_go_species(species):
      window["go_value"].update(value=0, range=(0, male_cnt - go_cnt))
    else:
      window["go_value"].update(value=0, range=(0, 0))
  if changing in ("male", "female", "go_value", None):
    diamond_gender = config.get_diamond_gender(species)    
    if diamond_gender == "both":
      window["diamond_value"].update(value=0, range=(0, male_cnt + female_cnt - diamond_cnt))
    elif diamond_gender == "male":
      window["diamond_value"].update(value=0, range=(0, male_cnt - go_cnt - diamond_cnt))
    elif diamond_gender == "female":
      window["diamond_value"].update(value=0, range=(0, female_cnt - diamond_cnt))   
     
    
def _parse_animal_row(animal_description: list, diamond_gender: str) -> Animal:
  animal_gender = animal_description[2]
  animal_weight = animal_description[3]
  animal_score = animal_description[4]
  animal_fur = animal_description[5] if animal_description[5] != "-" else None
  animal_go = animal_description[-1] == config.YES
  return Animal(animal_gender, animal_weight, animal_score, animal_fur, animal_go, diamond_gender)

def _parse_animal_details(values: dict, diamond_gender: str) -> Animal:
  return Animal(values["animal_gender"], values["animal_weight"], values["animal_score"], values["animal_fur"], values["animal_go"] == config.YES, diamond_gender)

def _update_animal_details(window: sg.Window, species: str, animal: Animal) -> None:  
  species_config = config.get_species(species)
  go_species = config.valid_go_species(species)

  if animal.go:
    low_weight = species_config["go"]["weight_low"]
    high_weight = species_config["go"]["weight_high"]
    low_score = species_config["go"]["score_low"]
    high_score = species_config["go"]["score_high"]
    window["animal_gender"].update(config.MALE, disabled=True)
  else:
    low_weight = round(species_config["diamonds"]["levels"][0][0], 1)
    high_weight = round(species_config["diamonds"]["weight_high"], 1)
    low_score = 0
    high_score = round(species_config["diamonds"]["score_high"], 1)
    window["animal_gender"].update(animal.gender, disabled=False)
    
    diamond_low_weight = round(species_config["diamonds"]["weight_low"], 1)
    diamond_low_score = round(species_config["diamonds"]["score_low"], 1)

  if go_species:
    window["animal_go"].update(disabled=False)
  else:
    window["animal_go"].update(config.NO, disabled=True)

  window["animal_go"].update(config.YES if animal.go else config.NO)     
  window["animal_weight"].update(value = animal.weight, range=(low_weight, high_weight))
  window["animal_score"].update(value = animal.score, range=(low_score, high_score))
  if animal.can_be_diamond and not animal.go:
    window["animal_weight_info"].update(f"(diamond weight: {diamond_low_weight})")
    window["animal_score_info"].update(f"(diamond score: {diamond_low_score})")
  else:
    window["animal_weight_info"].update(f"")
    window["animal_score_info"].update(f"")     
    
  animal_fur_names, _ = config.get_species_fur_names(species, animal.gender_key, go=animal.go)
  window["animal_fur"].update(animal.fur, values=animal_fur_names) 

def _show_animals(window: sg.Window, values: dict, reserve_key: str, species: str, species_name: str, modded: bool = False) -> tuple:
  is_modded = values["modded_reserves"] or modded
  is_top = values["top_scores"]  
  window['reserve_warning'].update(visible=False)
  try:
    reserve_details = adf.load_reserve(reserve_key, mod=is_modded)
  except adf.FileNotFound as ex:
    _show_error(window, ex)
    return
  window["progress"].update(30)
  if values["all_reserves"]:            
    species_description_full = populations.find_animals(species, modded=is_modded, good=values["good_ones"], top=is_top)            
  else:
    species_description_full = populations.describe_animals(reserve_key, species, reserve_details.adf, good=values["good_ones"], top=is_top)
  species_description = [x[0:-1] for x in species_description_full]
  animal_details = [x[-1:len(x)][0] for x in species_description_full]
  window["progress"].update(60)
  window["species_description"].update(species_description)
  window["progress"].update(100)
  _show_species_description(window, reserve_key, species_name, is_modded, is_top)        
  time.sleep(PROGRESS_DELAY)
  window["progress"].update(0)
  return species_description, animal_details

def _parse_species_groups(species_groups: dict, species_key: str):
  global species_group_details
  global male_group_cnt
  global female_group_cnt
    
  species_group_details = species_groups[species_key]
  male_group_cnt = len(species_group_details["male"])
  female_group_cnt = len(species_group_details["female"])  
  
def _toggle_section_visible(window: sg.Window, section: str, visible: bool = None) -> bool:
  opened = visible if visible != None else not window[section].visible
  window[f"{section}_symbol"].update(f"{symbol_open if opened else symbol_closed}")
  window[section].update(visible=opened)      
  return opened
  

def main_window(my_window: sg.Window = None) -> sg.Window:
    global reserve_names
    reserve_names = config.reserves()
    global reserve_name_size
    reserve_name_size = len(max(reserve_names, key = len))
    reserve_name_size = 27 if reserve_name_size < 27 else reserve_name_size

    global VIEW_MODDED
    VIEW_MODDED=f"({config.VIEWING_MODDED})"
    global VIEW_MOD_LOADED
    VIEW_MOD_LOADED=f"({config.VIEWING_LOADED_MOD})"

    global RESERVE_COLUMNS
    RESERVE_COLUMNS = [
        config.SPECIES, 
        config.ANIMALS_TITLE,
        config.MALES,
        config.FEMALES,
        config.HIGH_WEIGHT,
        config.HIGH_SCORE, 
        config.DIAMOND, 
        config.GREATONE 
    ]
    global SPECIES_COLUMNS
    SPECIES_COLUMNS = [
      config.RESERVE,
      config.LEVEL,
      config.GENDER,
      config.WEIGHT,
      config.SCORE,
      config.FUR,
      config.DIAMOND,
      config.GREATONE
    ]  
  
    layout = [
        [
          sg.Image(logo.value), 
          sg.Column([
            [sg.T(config.APC, expand_x=True, font="_ 24")],
            [sg.T(save_path_value, font=SMALL_FONT, k="save_path")]
          ]), 
          sg.Push(),
          sg.T(f"{config.VERSION}: {__version__} ({config.DEFAULT}: {config.default_locale}, {config.USING}: {config.use_languages[0]})", font=SMALL_FONT, p=((0,0),(0,60)), right_click_menu=['',[f'{config.UPDATE_TRANSLATIONS}::update_translations', config.SWITCH_LANGUAGE, [f"{x}::switch_language" for x in config.SUPPORTED_LANGUAGES]]])
        ],
        [
          sg.Column([[sg.T(f"{config.HUNTING_RESERVE}:", p=((0,10), (10,0))), 
                      sg.Combo(reserve_names, s=(reserve_name_size,len(reserve_names)), k="reserve_name", enable_events=True, metadata=reserve_keys, p=((0,0), (10,0)))
                    ]]),          
          sg.Column([[sg.Button(config.BACK_TO_RESERVE, k="show_reserve", font=SMALL_FONT, visible=False, p=((0,0), (10,0)))]]),          
        ],
        [
          sg.Column([
            [
              sg.Column([[sg.Checkbox(config.VIEW_MODDED_VERSION, k="load_modded", font=MEDIUM_FONT, enable_events=True, p=((0,0), (5,0)))]], p=(0,0)), 
              sg.Column([[sg.T("", text_color="orange", k="reserve_warning", font=MEDIUM_FONT, p=((5,0), (5,0)))]], p=(0,0)),
              sg.Column([[sg.T("", k="species_name", text_color="orange", justification="r", expand_x=True, p=((0,0),(0,0)))]], expand_x=True, p=(0,0))
            ]        
          ], expand_x=True)
        ],
        [sg.Column([
          [
            sg.Table(
              [], 
              RESERVE_COLUMNS, 
              expand_x=True, 
              k="reserve_description", 
              font=MEDIUM_FONT, 
              hide_vertical_scroll=True,
              col_widths=[16,7,5,7,11,10,8,10],
              auto_size_columns=False,
              header_background_color="brown",
              enable_click_events=True,
              expand_y=True,
              cols_justification=("l", "r", "r", "r", "r", "r", "r", "r")
            ), 
            sg.Table(
              [], 
              SPECIES_COLUMNS, 
              expand_x=True, 
              k="species_description", 
              font=MEDIUM_FONT, 
              header_background_color="brown",
              visible=False,
              col_widths=[17,7,3,3,3,9,4,4],
              auto_size_columns=False,
              expand_y=True,
              cols_justification=("l", "l", "c", "r", "r", "l", "c", "c"),
              enable_click_events=True
            ),
            sg.Table(
              [], 
              [config.RESERVE, config.LOADED, config.MODDED_FILE],
              font=MEDIUM_FONT, 
              header_background_color="brown",              
              expand_x=True, 
              expand_y=True, 
              k="mod_list", 
              col_widths=[17, 4, 50],
              auto_size_columns=False,
              visible=False,
              cols_justification=("l", "c", "l"),
              enable_click_events=True
            )
          ],
          [
            sg.ProgressBar(100, orientation='h', expand_x=True, s=(20,20), key='progress')
          ]
        ], expand_x=True, expand_y=True),
          sg.Column([[
            sg.TabGroup([[
              sg.Tab(config.MOD, [
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.T(textwrap.fill(config.MODIFY_ANIMALS, 30), font=MEDIUM_FONT, expand_x=True, justification="c", text_color="orange", p=((10,0),(0,10)))],
                [sg.Column([
                  [sg.T(symbol_closed, k="gender_section_symbol", enable_events=True, text_color="orange"), sg.T("Gender Counts", k="gender_section_title", enable_events=True, text_color="orange")],
                  [sg.pin(sg.Column([
                    [sg.T("F", font=DEFAULT_FONT, p=((10, 5), (20,0))), sg.Slider((0,0), orientation="h", expand_x=True, k="gender_value", enable_events=True), sg.T("M", font=DEFAULT_FONT, p=((5, 10), (20,0)))],              
                    [sg.T("0", p=((10, 0), (0, 0)), k="new_female_value"), sg.Push(), sg.T("0", p=((0, 10), (0, 0)), k="new_male_value")],
                  ], k="gender_section", visible=False))],
                  [sg.T(symbol_open, k="trophy_section_symbol", text_color="orange"), sg.T("Trophy Rating", k="trophy_section_title", enable_events=True, text_color="orange")],
                  [sg.pin(sg.Column([                  
                    [sg.T(f"{config.GREATONES}:", font=DEFAULT_FONT, p=((10,0),(0,10)))],
                    [sg.Slider((0,0), orientation="h", p=((20,10),(0,10)), k="go_value", enable_events=True)],                  
                    [sg.T(f"{config.DIAMONDS}:", font=DEFAULT_FONT, p=((10,0),(0,10))), sg.T("", p=((0,0),(0,10)), k="diamond_gender", font=MEDIUM_FONT, text_color="orange")],
                    [sg.Checkbox(config.USE_ALL_FURS, k="diamond_all_furs", font=MEDIUM_FONT, p=((20,10),(0,10)))],
                    [sg.Listbox([], k="diamond_furs", expand_x=True, p=((20,10),(0,10)), s=(None, 4), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],                  
                    [sg.Slider((0,0), orientation="h", p=((20,10),(0,20)), k="diamond_value", enable_events=True)],  
                  ], k="trophy_section", visible=True))]
                ] , expand_x=True, p=(0,0))],   
                [sg.T(" ", font="_ 3", p=(0,0))],             
                [sg.Button(config.RESET, k="reset", font=BUTTON_FONT), sg.Button(config.UPDATE_ANIMALS, expand_x=True, disabled=True, k="update_animals", font=BUTTON_FONT)],
                [sg.T(" ", font="_ 3", p=(0,0))],
              ], k="mod_tab"),
              sg.Tab(config.FURS, [
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.T(textwrap.fill(config.MODIFY_ANIMAL_FURS, 30), font=MEDIUM_FONT, expand_x=True, justification="c", text_color="orange", p=((10,0),(0,10)))],
                [sg.T(symbol_open, k="fur_male_section_symbol", enable_events=True, text_color="orange"), sg.T(config.MALE_FURS, k="fur_male_section_title", enable_events=True, text_color="orange")],
                [sg.pin(sg.Column([
                    [sg.Checkbox(config.USE_ALL_FURS, k="male_all_furs", font=MEDIUM_FONT, p=((10,0),(0,0)))],
                    [sg.Listbox([], k="male_furs", expand_x=True, p=((10,10),(0,0)), s=(None, 4), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],
                    [sg.Slider((0,0), orientation="h", p=((10,10),(10,20)), k="male_fur_animals_cnt")],                        
                ], k="fur_male_section", visible=True))],
                [sg.T(symbol_closed, k="fur_female_section_symbol", enable_events=True, text_color="orange"), sg.T(config.FEMALE_FURS, k="fur_female_section_title", enable_events=True, text_color="orange")],
                [sg.pin(sg.Column([            
                  [sg.Checkbox(config.USE_ALL_FURS, k="female_all_furs", font=MEDIUM_FONT, p=((10,0),(0,0)))],
                  [sg.Listbox([], k="female_furs", expand_x=True, p=((10,10),(0,0)), s=(None, 4), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],
                  [sg.Slider((0,0), orientation="h", p=((10,10),(10,20)), k="female_fur_animals_cnt")],                  
                ], k="fur_female_section", visible=False))],
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.Button(config.RESET, k="fur_reset", font=BUTTON_FONT, p=((10,0),(0,0))), sg.Button(config.UPDATE_ANIMALS, expand_x=True, disabled=True, k="fur_update_animals", font=BUTTON_FONT, p=((10,10),(0,0)))],
                [sg.T(" ", font="_ 3", p=(0,0))]                
              ], k="fur_tab"),
              sg.Tab(config.PARTY, [
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.T(textwrap.fill(config.CHANGE_ALL_SPECIES, 30), font=MEDIUM_FONT, expand_x=True, justification="c", text_color="orange", p=((10,0),(0,10)))],
                [sg.Button(config.GREATONE_PARTY, expand_x=True, disabled=True, k="go_party", font=BUTTON_FONT, button_color=(sg.theme_button_color()[1], "brown"))],
                [sg.Button(config.DIAMOND_PARTY, expand_x=True, disabled=True, k="diamond_party", font=BUTTON_FONT, button_color=(sg.theme_button_color()[1], "brown"))],
                [sg.Button(config.WE_ALL_PARTY, expand_x=True, disabled=True, k="everyone_party", font=BUTTON_FONT, button_color=(sg.theme_button_color()[1], "brown"))],
                [sg.Button(config.FUR_PARTY, expand_x=True, disabled=True, k="fur_party", font=BUTTON_FONT, button_color=(sg.theme_button_color()[1], "brown"))]
              ], k="party_tab"),
              sg.Tab(config.EXPLORE, [
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.T(textwrap.fill(config.EXPLORE_ANIMALS, 30), font=MEDIUM_FONT, expand_x=True, justification="c", text_color="orange", p=((10,0),(0,10)))],
                [sg.Checkbox(config.DIAMONDS_AND_GREATONES, font=MEDIUM_FONT, default=False, k="good_ones")],
                [sg.Checkbox(config.LOOK_MODDED_ANIMALS, font=MEDIUM_FONT, k="modded_reserves")],
                [sg.Checkbox(config.LOOK_ALL_RESERVES, font=MEDIUM_FONT, k="all_reserves")],
                [sg.Checkbox(config.ONLY_TOP_SCORES, font=MEDIUM_FONT, k="top_scores")],
                [sg.Button(config.SHOW_ANIMALS, expand_x=True, k="show_animals", disabled=True, font=BUTTON_FONT)]
              ], k="explore_tab"),
              sg.Tab(config.FILES, [
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.T(textwrap.fill(config.MANAGE_MODDED_RESERVES, 30), font=MEDIUM_FONT, expand_x=True, justification="c", text_color="orange", p=((10,0),(0,10)))],
                [sg.Button(config.CONFIGURE_GAME_PATH, expand_x=True, k="set_save", font=BUTTON_FONT)],
                [sg.Button(config.LIST_MODS, expand_x=True, k="list_mods", font=BUTTON_FONT)],
                [sg.Button(config.LOAD_MOD, expand_x=True, k="load_mod", disabled=True, font=BUTTON_FONT)],
                [sg.Button(config.UNLOAD_MOD, expand_x=True, k="unload_mod", disabled=True, font=BUTTON_FONT)],
                [sg.Button(config.EXPORT_MOD, expand_x=True, k="export_mod", disabled=True, font=BUTTON_FONT)],
                [sg.Button(config.IMPORT_MOD, expand_x=True, k="import_mod", disabled=True, font=BUTTON_FONT)],
              ])
            ]], p=(0,5))
          ]], vertical_alignment="top", p=(0,0), k="modding"),
          sg.Column([[
            sg.Frame(None, [
              [sg.T(" ", font="_ 3", p=(0,0))],
              [sg.T(textwrap.fill(config.ANIMAL_DETAILS, 30), font=MEDIUM_FONT, expand_x=True, justification="c", text_color="orange", p=((10,0),(0,10)))],
              [sg.T(f"{config.GREATONE}:", p=((10,0),(0,0)))],
              [sg.Combo([config.YES, config.NO], None, p=((20,0),(10,0)), k="animal_go", enable_events=True, disabled=True)],
              [sg.T(f"{config.GENDER}:", p=((10,0),(10,0)))],
              [sg.Combo([config.MALE, config.FEMALE], None, p=((20,0),(10,0)), k="animal_gender", enable_events=True, disabled=True)],
              [sg.T(f"{config.WEIGHT}:", p=((10,0),(10,0))), sg.T("", p=((0,0),(10,0)), k="animal_weight_info", font=MEDIUM_FONT, text_color="orange")],
              [sg.Slider((0,0), orientation="h", resolution=0.1, p=((20,10),(10,0)), k="animal_weight")],
              [sg.T(f"{config.SCORE}:", p=((10,0),(10,0))), sg.T("", p=((0,0),(10,0)), k="animal_score_info", font=MEDIUM_FONT, text_color="orange")],
              [sg.Slider((0,0), orientation="h", resolution=0.1, p=((20,10),(10,0)), k="animal_score")],              
              [sg.T(f"{config.FUR}:", p=((10,0),(10,0))), sg.T(f"({config.RANDOM_FUR})", p=((0,0),(10,0)), font=MEDIUM_FONT, text_color="orange")],
              [sg.Combo([],  p=((20,10),(10,20)), k="animal_fur", expand_x=True, disabled=True)],
              [sg.Button(config.RESET, k="animal_reset", font=BUTTON_FONT), sg.Button(config.UPDATE_ANIMAL, expand_x=True, disabled=True, k="update_animal", font=BUTTON_FONT)],                
              [sg.T(" ", font="_ 3", p=(0,0))]
            ], relief=sg.RELIEF_RAISED, p=(0,5))
        ]], k="exploring", vertical_alignment="top", p=(0,0), visible=False)        
        ],               
        [
          sg.T("", text_color="orange", k="reserve_note")
        ]
    ]

    window = sg.Window(config.APC, layout, resizable=True, font=DEFAULT_FONT, icon=logo.value, size=(1300, 780))
    
    if my_window is not None:
      my_window.close()
    return window
    
def main() -> None:
  sg.theme("DarkAmber")
    
  window = main_window()
  reserve_details = None
  global reserve_description
  global species_group_details
  global male_group_cnt
  global female_group_cnt

  while True:
      event, values = window.read()
      # print(event, values, "\n")

      if event == sg.WIN_CLOSED:
          break 
      
      try:
        reserve_name = values["reserve_name"] if "reserve_name" in values else None
        if event == "reserve_name" and reserve_name:
          _show_reserve_description(window)    
          reserve_key = _reserve_key_from_name(reserve_name)    
          is_modded = values["load_modded"]
          if is_modded:
            window["reserve_warning"].update(VIEW_MODDED)            
          else:
            window["reserve_warning"].update(VIEW_MOD_LOADED if _is_reserve_mod_loaded(reserve_key, window) else "")
          window["reserve_note"].update("")   
          try:
            reserve_details = adf.load_reserve(reserve_key, mod=is_modded)
            window["progress"].update(50)            
          except adf.FileNotFound as ex:
            _show_error(window, ex)    
            reserve_details = None
            window["reserve_description"].update([])
            window["go_party"].update(disabled=True)
            window["diamond_party"].update(disabled=True)
            window["everyone_party"].update(disabled=True)
            window["fur_party"].update(disabled=True)              
            window["show_animals"].update(disabled=True)              
            continue
          reserve_description, species_groups = populations.describe_reserve(reserve_key, reserve_details.adf)
          _disable_go_parties(window, reserve_key)
          window["diamond_party"].update(disabled=False)
          window["everyone_party"].update(disabled=False)
          window["fur_party"].update(disabled=False)
          window["progress"].update(90)
          window["reserve_description"].update(_highlight_values(_format_reserve_description(reserve_description)))
          window["progress"].update(100)
          time.sleep(PROGRESS_DELAY)
          window["progress"].update(0)
          _disable_new_reserve(window)
        elif isinstance(event, tuple):
          if event[0] == "reserve_description" and event[1] == "+CLICKED+" and reserve_name:
            row, _ = event[2]
            if row != None and row >= 0:
              window["update_animals"].update(disabled=False)
              species_name = reserve_description[row][2] if reserve_description else ""
              species = reserve_description[row][0] if reserve_description else ""              
              window["reserve_note"].update("")
              _disable_go(window, True)
              _disable_furs(window, True)
              _disable_diamonds(window, False)
              window["show_animals"].update(disabled=False)
              if valid_go_species(species):
                _disable_go(window, False)
              if valid_fur_species(species):
                _disable_furs(window, False)

              great_one_cnt = int(reserve_description[row][-1])
              diamond_cnt = int(reserve_description[row][-2])
              total_cnt = int(reserve_description[row][3])
              male_cnt = int(reserve_description[row][4])
              female_cnt = int(reserve_description[row][5])
              
              _parse_species_groups(species_groups, species)
              _update_mod_animal_counts(window, species, total_cnt, male_cnt, female_cnt, female_cnt, male_cnt, great_one_cnt, diamond_cnt, male_group_cnt, female_group_cnt)
              
              male_fur_names, male_fur_keys = config.get_species_fur_names(species, "male")
              female_fur_names, female_fur_keys = config.get_species_fur_names(species, "female")
              diamond_gender = get_diamond_gender(species)
              window["male_furs"].update(values=male_fur_names)
              window["female_furs"].update(values=female_fur_names)
              window["male_fur_animals_cnt"].update(value = 0, range=(0, male_cnt - great_one_cnt)) 
              window["female_fur_animals_cnt"].update(value = 0, range=(0, female_cnt))
              window["male_all_furs"].update(False)
              window["female_all_furs"].update(False)
              if diamond_gender == "male":
                window["diamond_furs"].update(values=male_fur_names)
                window["diamond_gender"].update(f"({config.MALES.lower()})")
              elif diamond_gender == "female":
                window["diamond_furs"].update(values=male_fur_names)
                window["diamond_gender"].update(f"({config.FEMALES.lower()})")   
              else:
                male_labeled = [f"{x} ({config.MALE.lower()})" for x in male_fur_names]
                female_labeled = [f"{x} ({config.FEMALE.lower()})" for x in female_fur_names]
                window["diamond_furs"].update(values=male_labeled+female_labeled)
                window["diamond_gender"].update(f"({config.MALES.lower()} and {config.FEMALES.lower()})")                                
          elif event[0] == "mod_list" and event[1] == "+CLICKED+":
            row, _ = event[2]
            if row != None and row >= 0:
              selected_mod = mods[row]
              window["load_mod"].update(disabled=False)
              window["export_mod"].update(disabled=False)
              window["import_mod"].update(disabled=False)
              window["unload_mod"].update(disabled=selected_mod[1] != config.YES) 
          elif event[0] == "species_description" and event[1] == "+CLICKED+":
            animal_row, _ = event[2]
            if animal_row != None and animal_row >= 0:                                       
              animal = _parse_animal_row(species_description[animal_row], get_diamond_gender(species))
              print("Visual Seed:", animal_details[animal_row].visual_seed)
              _disable_animal_details(window, False)
              _update_animal_details(window, species, animal)
        elif event == "animal_go" or event == "animal_gender":
          updated_animal = _parse_animal_details(values, get_diamond_gender(species))
          updated_animal.fur = None
          _update_animal_details(window, species, updated_animal)         
        elif event == "set_save":
          provided_path = sg.popup_get_folder(f"{config.SELECT_FOLDER}:", title=config.SAVES_PATH_TITLE, icon=logo.value, font=DEFAULT_FONT)
          if provided_path:
            save_path(provided_path)
            window["save_path"].update(provided_path)
            window["reserve_note"].update(config.PATH_SAVED)
        elif event == "show_animals":
          species_description, animal_details = _show_animals(window, values, reserve_key, species, species_name)
        elif event == "show_reserve":
          _show_reserve_description(window)
        elif event == "update_animal":
          selected_animal_rows = window["species_description"].SelectedRows
          if len(selected_animal_rows) > 0:
            full_animal_details = animal_details[selected_animal_rows[0]]
            _mod_animal(window, reserve_key, species, _parse_animal_details(values, get_diamond_gender(species)), full_animal_details)
            species_description, animal_details = _show_animals(window, values, reserve_key, species, species_name, modded=True)
        elif event == "update_animals":
          male_value = int(window["new_male_value"].DisplayText)
          female_value = int(window["new_female_value"].DisplayText)
          go_value = int(values["go_value"])
          diamond_value = int(values["diamond_value"])
          diamond_all_furs = values["diamond_all_furs"]
          diamond_furs = window["diamond_furs"].Values if diamond_all_furs or len(values["diamond_furs"]) == 0 else values["diamond_furs"]
          if diamond_gender == "male":
            male_use_furs = [male_fur_keys[male_fur_names.index(x)] for x in diamond_furs]
            female_use_furs = []
          elif diamond_gender == "female":
            male_use_furs = []
            female_use_furs = [female_fur_keys[female_fur_names.index(x)] for x in diamond_furs]
          else:
            label_pattern = r'\s\(\w+\)$'
            male_use_furs = [male_fur_keys[male_fur_names.index(re.sub(label_pattern, "", x))] for x in diamond_furs if f"({config.MALE.lower()})" in x]
            female_use_furs = [female_fur_keys[female_fur_names.index(re.sub(label_pattern, "", x))] for x in diamond_furs if f"({config.FEMALE.lower()})" in x]

          if male_value > male_cnt:
            print("modding males")
            _mod(reserve_key, species, Strategy.males, window, male_value - male_cnt, False)  
          if female_value > female_cnt:
            print("modding females")
            _mod(reserve_key, species, Strategy.females, window, female_value - female_cnt, False)                         
          if _is_go_enabled(window, go_value):
            print("modding go")
            _mod(reserve_key, species, Strategy.go_some, window, go_value, False)        
          if _is_diamond_enabled(window, diamond_value):
            print("modding diamonds")
            _mod_diamonds(window, reserve_key, species, diamond_value, male_use_furs, female_use_furs)
            
          _disable_new_reserve(window)   
          male_cnt = 0
          female_cnt = 0
          _reset_mod(window)   
          _clear_furs(window) 
        elif event == "fur_update_animals":
          male_all_furs = values["male_all_furs"]
          female_all_furs = values["female_all_furs"]
          male_furs = male_fur_names if male_all_furs else values["male_furs"]
          male_furs = [male_fur_keys[male_fur_names.index(x)] for x in male_furs]
          female_furs = female_fur_names if female_all_furs else values["female_furs"]
          female_furs = [female_fur_keys[female_fur_names.index(x)] for x in female_furs]
          male_fur_cnt = int(values["male_fur_animals_cnt"])
          female_fur_cnt = int(values["female_fur_animals_cnt"])
          male_changing = (male_all_furs or len(male_furs) > 0) and male_fur_cnt > 0
          female_changing = (female_all_furs or len(female_furs) > 0) and female_fur_cnt > 0
          if male_changing or female_changing:
            _mod_furs(window, reserve_key, species, male_furs, female_furs, male_fur_cnt, female_fur_cnt)
        elif event == "fur_reset":
          _reset_furs(window)
        elif event == "animal_reset":
          selected_animal_rows = window["species_description"].SelectedRows
          if len(selected_animal_rows) > 0:
            animal = _parse_animal_row(species_description[selected_animal_rows[0]], get_diamond_gender(species))
            _update_animal_details(window, species, animal)
        elif event == "load_modded":
          window["modded_reserves"].update(values["load_modded"])  
        elif event == "list_mods":
          mods = _process_list_mods(window, reserve_name)
        elif event == "load_mod":
          confirm = _show_popup(f"{config.CONFIRM_LOAD_MOD} \n\n{config.BACKUP_WILL_BE_MADE}\n", config.CONFIRMATION, config.OK, config.CANCEL)
          if confirm == "ok":
            _load_mod(window, selected_mod[2])
            mods = _process_list_mods(window)
        elif event == "unload_mod":
          _unload_mod(window, selected_mod[2])
          mods = _process_list_mods(window)
        elif event == "export_mod":
          from_mod = selected_mod[2]
          export_file = _show_export_popup(selected_mod[0], Path(from_mod).name)
          if export_file != None and export_file != "cancel":
            _copy_file(from_mod, export_file)
            sg.PopupQuickMessage(config.MOD_EXPORTED, font="_ 28", background_color="brown")
        elif event == "import_mod":
          to_mod = selected_mod[2]
          import_file = _show_import_popup(selected_mod[0], Path(to_mod).name)
          if import_file != '' and import_file != "cancel":
            _copy_file(import_file, to_mod)
            sg.PopupQuickMessage(config.MOD_IMPORTED, font="_ 28", background_color="brown")
        elif event == "reset":
          male_cnt = 0
          female_cnt = 0
          _reset_mod(window)
        elif event == "go_party":
          go_species = _get_go_species(reserve_key)
          for species in go_species:
            _mod(reserve_key, species, Strategy.males, window, 100, rares=False, percentage=True)
            _mod(reserve_key, species, Strategy.go_all, window, 100, rares=False, percentage=True)
          _disable_new_reserve(window)
        elif event == "diamond_party":
          for species in get_reserve_species(reserve_key):
            diamond_gender = get_diamond_gender(species)
            if diamond_gender == "male":
              _mod(reserve_key, species, Strategy.males, window, 100, rares=True, percentage=True)
            elif diamond_gender == "female":
              _mod(reserve_key, species, Strategy.females, window, 100, rares=True, percentage=True)
            _mod(reserve_key, species, Strategy.diamond_all, window, 100, rares=True, percentage=True)
          _disable_new_reserve(window)
        elif event == "everyone_party":
          go_species = _get_go_species(reserve_key)
          for species in get_reserve_species(reserve_key):
            if species in go_species:
              _mod(reserve_key, species, Strategy.go_some, window, 10, rares=False, percentage=True)
            _mod(reserve_key, species, Strategy.diamond_some, window, 50, rares=True, percentage=True)
            _mod(reserve_key, species, Strategy.furs_some, window, 100, rares=True, percentage=True)
          _disable_new_reserve(window)
        elif event == "fur_party":
          for species in get_reserve_species(reserve_key):
            _mod(reserve_key, species, Strategy.furs_some, window, 100, rares=True, percentage=True)
        elif "::" in event:
          value, key = event.split("::")
          if key == "update_translations":
            subprocess.Popen(f"pybabel compile --domain=apc --directory={config.APP_DIR_PATH / 'locale'}", shell=True)
            _show_popup(config.PLEASE_RESTART, config.APC, config.OK)
          elif key == "switch_language":
            config.update_language(value)
            window = main_window(window)
        elif event in ("gender_value", "go_value", "diamond_value"):
          new_go_cnt = int(values["go_value"])
          gender_value = int(values["gender_value"])
          new_male_cnt = gender_value + male_cnt if gender_value > 0 else male_cnt - (-gender_value)
          new_female_cnt = -gender_value + female_cnt if gender_value < 0 else female_cnt - gender_value
          if event == "gender_value":
            changing = "male" if gender_value > 0 else "female"
          else:
            changing = event
          _update_mod_animal_counts(window, species, total_cnt, male_cnt, female_cnt, new_female_cnt, new_male_cnt, new_go_cnt, diamond_cnt, male_group_cnt, female_group_cnt, changing=changing)
        elif event == "gender_section_symbol" or event == "gender_section_title":
          if not window["gender_section"].visible:
            _toggle_section_visible(window, "gender_section", True)
            _toggle_section_visible(window, "trophy_section", False)            
        elif event == "trophy_section_symbol" or event == "trophy_section_title":
          if not window["trophy_section"].visible:
            _toggle_section_visible(window, "gender_section", False)
            _toggle_section_visible(window, "trophy_section", True) 
        elif event == "fur_male_section_symbol" or event == "fur_male_section_title":
          if not window["fur_male_section"].visible:
            _toggle_section_visible(window, "fur_male_section", True)
            _toggle_section_visible(window, "fur_female_section", False)    
        elif event == "fur_female_section_symbol" or event == "fur_female_section_title":
          if not window["fur_female_section"].visible:
            _toggle_section_visible(window, "fur_male_section", False)
            _toggle_section_visible(window, "fur_female_section", True)                           
      except Exception:
        _show_error_window(traceback.format_exc())
  
  window.close()  

if __name__ == "__main__":
    main()