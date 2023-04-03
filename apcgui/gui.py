import PySimpleGUI as sg
import sys, traceback, time, os, re, shutil, subprocess
from apc import populations, adf, config
from apc.config import valid_go_species, Strategy, MOD_DIR_PATH, save_path, get_save_path, get_population_file_name, get_population_name, BACKUP_DIR_PATH, valid_fur_species, format_key, get_reserve_species, get_diamond_gender, get_species_name
from apcgui import __version__, logo, use_languages
from typing import List
from pathlib import Path

DEFAULT_FONT = "_ 14"
MEDIUM_FONT = "_ 13"
BUTTON_FONT = "_ 13"
SMALL_FONT = "_ 11"
PROGRESS_DELAY = 0.3
VIEW_MODDED=f"({config.VIEWING_MODDED})"

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
SPECIES_COLUMNS = [
  config.RESERVE,
  config.LEVEL,
  config.GENDER,
  config.WEIGHT,
  config.SCORE,
  config.VISUALSEED,
  config.FUR,
  config.DIAMOND,
  config.GREATONE
]

reserve_keys = config.reserve_keys()
reserve_names = config.reserves()
reserve_name_size = len(max(reserve_names, key = len))
save_path_value = get_save_path()

def _progress(window: sg.Window, value: int) -> None:
 window["progress"].update(int)   

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
  window["male_value"].update(disabled = disabled)
  window["female_value"].update(disabled = disabled)

def _disable_furs(window: sg.Window, disabled: bool) -> None:
  window["rare_fur_value"].update(disabled = disabled)
  window["furs"].update(disabled = disabled)
  window["others"].update(disabled = disabled)
  window["diamonds"].update(disabled = disabled)
  if disabled:
    window["furs"].update(False)

def _disable_go(window: sg.Window, disabled: bool) -> None:
  window["great_ones"].update(disabled = disabled)  
  window["go_value"].update(disabled = disabled)

def _disable_new_reserve(window: sg.Window) -> None:
  _disable_diamonds(window, True)
  _disable_furs(window, True)
  _disable_go(window, True)  
  window["show_animals"].update(disabled=True)
  window["update_animals"].update(disabled=True)

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

def _species_key_from_name(reserve_key: str, row: int) -> str:
  return get_reserve_species(reserve_key)[row]

def _show_species_description(window: sg.Window, species_name: str, is_modded: bool) -> None:
    window["reserve_description"].update(visible=False)
    window["modding"].update(visible=False)
    window["species_description"].update(visible=True)
    window["show_reserve"].update(visible=True)
    window["species_name"].update(f"{species_name.upper()}{f' ({config.MODDED})' if is_modded else ''}")
    window["mod_list"].update(visible=False)

def _show_reserve_description(window: sg.Window) -> None:
    window["reserve_description"].update(visible=True)
    window["modding"].update(visible=True)
    window["species_description"].update(visible=False)
    window["show_reserve"].update(visible=False)
    window["species_name"].update("")
    window['reserve_warning'].update(visible=True)   
    window["mod_list"].update(visible=False) 
    window["mod_tab"].update(disabled=False)
    window["mod_tab"].select()
    window["explore_tab"].update(disabled=False)    
    window["party_tab"].update(disabled=False)
    window["reserve_note"].update("")
    window["load_mod"].update(disabled=True)
    window["unload_mod"].update(disabled=True)    

def _show_mod_list(window: sg.Window) -> None:
  window["reserve_description"].update(visible=False)
  window["mod_list"].update(visible=True)
  window["show_reserve"].update(visible=True)
  window["mod_tab"].update(disabled=True)
  window["explore_tab"].update(disabled=True)
  window["party_tab"].update(disabled=True)
  window["load_mod"].update(disabled=True)
  window["unload_mod"].update(disabled=True)
  
def _viewing_modded(window: sg.Window) -> bool:
  return window['reserve_warning'].get() == VIEW_MODDED  

def _is_male_enabled(window: sg.Window, value: int) -> bool:
  return not window["male_value"].Disabled and value != 0 

def _is_female_enabled(window: sg.Window, value: int) -> bool:
  return not window["female_value"].Disabled and value != 0 

def _is_furs_enabled(window: sg.Window, value: int) -> bool:
  return not window["rare_fur_value"].Disabled and value != 0

def _is_diamond_enabled(window: sg.Window, value: int) -> bool:
  return not window["diamond_value"].Disabled and value != 0

def _is_go_enabled(window: sg.Window, value: int) -> bool:
  return not window["great_ones"].Disabled and value != 0

def _show_error(window: sg.Window, ex: adf.FileNotFound) -> None:
  window["progress"].update(0)      
  window["reserve_note"].update(f"{config.ERROR}: {ex}")      
  print("ERROR", traceback.print_exc(file=sys.stdout))   
   
def _show_warning(window: sg.Window, message: str) -> None:
  window["progress"].update(0)      
  window["reserve_note"].update(f"{config.WARNING}: {message}")

def _mod(reserve_key: str, species: str, strategy: Strategy, window: sg.Window, modifier: int, rares: bool, percentage: bool) -> None:
  print((reserve_key, species, strategy.value, modifier, rares, percentage))
  is_modded = _viewing_modded(window)
  try:
    reserve_details = adf.load_reserve(reserve_key, mod=is_modded)
  except Exception as ex:
    _show_error(window, ex)
    return
  window["progress"].update(25)
  try:
    modded_reserve_description = populations.mod(reserve_key, reserve_details, species, strategy.value, rares=rares, modifier=modifier, percentage=percentage)
  except Exception as ex:    
    _show_error(window, ex)
    return
  window["progress"].update(50)
  window["reserve_description"].update(_highlight_values(modded_reserve_description))
  window["progress"].update(75)
  window["reserve_warning"].update(VIEW_MODDED)
  window["reserve_note"].update(f"{get_species_name(species).upper()} ({format_key(strategy)}) {config.SAVED}: \"{MOD_DIR_PATH / get_population_file_name(reserve_key)}\"")
  window["progress"].update(100)
  time.sleep(PROGRESS_DELAY)
  window["progress"].update(0)  
  window["show_animals"].update(disabled=True)
  window["update_animals"].update(disabled=True)
  window["modded_reserves"].update(True)

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
      already_loaded = config.YES if already_loaded else "-"
      mods.append([get_population_name(item.name), already_loaded, item_path])
  return mods

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
    sg.PopupOK(config.MOD_LOADED, font=DEFAULT_FONT, icon=logo.value, title=config.MOD_LOADED)
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
    sg.PopupOK(config.MOD_UNLOADED, font=DEFAULT_FONT, icon=logo.value, title=config.MOD_UNLOADED)
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

def main():
    sg.theme("DarkAmber")

    layout = [
        [
          sg.Image(logo.value), 
          sg.Column([
            [sg.T(config.APC, expand_x=True, font="_ 24")],
            [sg.T(save_path_value, font=SMALL_FONT, k="save_path")],
          ]), 
          sg.Push(),
          sg.T(f"{config.VERSION}: {__version__} ({use_languages[0]})", font=SMALL_FONT, p=((0,0),(0,60)), right_click_menu=['',[f'{config.UPDATE_TRANSLATIONS}::update_translations']])
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
              col_widths=[17,7,2,4,4,7,9,4,4],
              auto_size_columns=False,
              expand_y=True,
              cols_justification=("l", "l", "c", "r", "r", "r", "l", "c", "c")
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
                [sg.Column([
                  [sg.Checkbox(config.UPDATE_BY_PERCENTAGE, k="by_percentage", font=MEDIUM_FONT)],
                  [sg.T(f"{config.MORE_MALES}:", font=DEFAULT_FONT, expand_x=True), sg.Input(s=4, default_text="0", k="male_value")],
                  [sg.T(f"{config.MORE_FEMALES}:", font=DEFAULT_FONT, expand_x=True), sg.Input(s=4, default_text="0", k="female_value")],
                  [sg.T(f"{config.GREATONES}:", font=DEFAULT_FONT, expand_x=True), sg.Input(s=4, default_text="0", k="go_value")],
                  [sg.T(f"{config.DIAMONDS}:", font=DEFAULT_FONT, expand_x=True), sg.Input(s=4, default_text="0", k="diamond_value")],
                  [sg.Checkbox(config.INCLUDE_RARE_FURS, k="furs", font=MEDIUM_FONT)],
                  [sg.T(f"{config.ALL_FURS}:", font=DEFAULT_FONT, expand_x=True), sg.Input(s=4, default_text="0", k="rare_fur_value")]
                ] , expand_x=True)],                
                [sg.Button(config.RESET, k="reset", font=BUTTON_FONT), sg.Button(config.UPDATE_ANIMALS, expand_x=True, disabled=True, k="update_animals", font=BUTTON_FONT)],
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.T(f"{config.JUST_FURS}:")],
                [sg.T(f"({config.ONE_OF_EACH_FUR})", font=SMALL_FONT, p=(5,0))],
                [sg.Button(config.GREATONES, expand_x=True, disabled=True, k="great_ones", font=BUTTON_FONT)],
                [sg.Button(config.DIAMONDS, expand_x=True, disabled=True, k="diamonds", font=BUTTON_FONT)],
                [sg.Button(config.OTHERS, expand_x=True, disabled=True, k="others", font=BUTTON_FONT)],
                [sg.T(" ", font="_ 3", p=(0,0))]
              ], k="mod_tab"),
              sg.Tab(config.PARTY, [
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.Button(config.GREATONE_PARTY, expand_x=True, disabled=True, k="go_party", font=BUTTON_FONT, button_color=(sg.theme_button_color()[1], "brown"))],
                [sg.Button(config.DIAMOND_PARTY, expand_x=True, disabled=True, k="diamond_party", font=BUTTON_FONT, button_color=(sg.theme_button_color()[1], "brown"))],
                [sg.Button(config.WE_ALL_PARTY, expand_x=True, disabled=True, k="everyone_party", font=BUTTON_FONT, button_color=(sg.theme_button_color()[1], "brown"))],
                [sg.Button(config.FUR_PARTY, expand_x=True, disabled=True, k="fur_party", font=BUTTON_FONT, button_color=(sg.theme_button_color()[1], "brown"))]
              ], k="party_tab"),
              sg.Tab(config.EXPLORE, [
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.Checkbox(config.DIAMONDS_AND_GREATONES, font=MEDIUM_FONT, default=True, k="good_ones")],
                [sg.Checkbox(config.LOOK_MODDED_ANIMALS, font=MEDIUM_FONT, k="modded_reserves")],
                [sg.Checkbox(config.LOOK_ALL_RESERVES, font=MEDIUM_FONT, k="all_reserves")],
                [sg.Checkbox(config.ONLY_TOP_SCORES, font=MEDIUM_FONT, k="top_scores")],
                [sg.Button(config.SHOW_ANIMALS, expand_x=True, k="show_animals", disabled=True, font=BUTTON_FONT)]
              ], k="explore_tab"),
              sg.Tab(config.FILES, [
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.Button(config.CONFIGURE_GAME_PATH, expand_x=True, k="set_save", font=BUTTON_FONT)],
                [sg.Button(config.LIST_MODS, expand_x=True, k="list_mods", font=BUTTON_FONT)],
                [sg.Button(config.LOAD_MOD, expand_x=True, k="load_mod", disabled=True, font=BUTTON_FONT)],
                [sg.Button(config.UNLOAD_MOD, expand_x=True, k="unload_mod", disabled=True, font=BUTTON_FONT)],
              ])
            ]], p=(0,5))
          ]], vertical_alignment="top", p=(0,0), k="modding")         
        ],               
        [
          sg.T("", text_color="orange", k="reserve_note")
        ]
    ]

    window = sg.Window(config.APC, layout, resizable=True, font=DEFAULT_FONT, icon=logo.value, size=(1200, 770))
    reserve_details = None
    
    while True:
        event, values = window.read()
        print(event, values)

        if event == sg.WIN_CLOSED:
            break 
        
        try:
          reserve_name = values["reserve_name"] if "reserve_name" in values else None
          if event == "reserve_name" and reserve_name:
            _show_reserve_description(window)        
            is_modded = values["load_modded"]
            if is_modded:
              window["reserve_warning"].update(VIEW_MODDED)            
            else:
              window["reserve_warning"].update("")
            window["reserve_note"].update("")   
            reserve_key = _reserve_key_from_name(reserve_name)
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
            reserve_description = populations.describe_reserve(reserve_key, reserve_details.adf)
            _disable_go_parties(window, reserve_key)
            window["diamond_party"].update(disabled=False)
            window["everyone_party"].update(disabled=False)
            window["fur_party"].update(disabled=False)
            window["progress"].update(90)
            window["reserve_description"].update(_highlight_values(reserve_description))
            window["progress"].update(100)
            time.sleep(PROGRESS_DELAY)
            window["progress"].update(0)
            _disable_new_reserve(window)
          elif isinstance(event, tuple):
            if event[0] == "reserve_description" and event[1] == "+CLICKED+" and reserve_name:
              row, _ = event[2]
              if row != None and row >= 0:
                window["update_animals"].update(disabled=False)
                species_name = reserve_description[row][0] if reserve_description else ""
                species = _species_key_from_name(reserve_key, row)
                print(f"species clicked: {species}")
                window["reserve_note"].update("")
                _disable_go(window, True)
                _disable_furs(window, True)
                _disable_diamonds(window, False)
                window["show_animals"].update(disabled=False)
                if valid_go_species(species):
                  _disable_go(window, False)
                if valid_fur_species(species):
                  _disable_furs(window, False)
            elif event[0] == "mod_list" and event[1] == "+CLICKED+":
              row, _ = event[2]
              if row != None and row >= 0:
                selected_mod = mods[row]
                window["load_mod"].update(disabled=False)
                window["unload_mod"].update(disabled=selected_mod[1] != config.YES)                
          elif event == "set_save":
            provided_path = sg.popup_get_folder(f"{config.SELECT_FOLDER}:", title=config.SAVES_PATH_TITLE, icon=logo.value, font=DEFAULT_FONT)
            if provided_path:
              save_path(provided_path)
              window["save_path"].update(provided_path)
              window["reserve_note"].update(config.PATH_SAVED)
          elif event == "show_animals":
            print((reserve_key, species))                  
            is_modded = values["modded_reserves"]
            is_top = values["top_scores"]
            window['reserve_warning'].update(visible=False)
            try:
              reserve_details = adf.load_reserve(reserve_key, mod=is_modded)
            except adf.FileNotFound as ex:
              _show_error(window, ex)
              continue
            window["progress"].update(30)
            if values["all_reserves"]:            
              species_description = populations.find_animals(species, modded=is_modded, good=values["good_ones"], top=is_top)
            else:
              species_description = populations.describe_animals(reserve_key, species, reserve_details.adf, good=values["good_ones"], top=is_top)
            window["progress"].update(60)
            window["species_description"].update(species_description)
            window["progress"].update(100)
            _show_species_description(window, species_name, is_modded)        
            time.sleep(PROGRESS_DELAY)
            window["progress"].update(0)
          elif event == "show_reserve":
            _show_reserve_description(window)
          elif event == "update_animals":
            use_percent = values["by_percentage"]
            male_value = int(values["male_value"]) if values["male_value"].isdigit() else 0
            female_value = int(values["female_value"]) if values["female_value"].isdigit() else 0
            go_value = int(values["go_value"]) if values["go_value"].isdigit() else 0
            diamond_value = int(values["diamond_value"]) if values["diamond_value"].isdigit() else 0
            rare_fur_value = int(values["rare_fur_value"]) if values["rare_fur_value"].isdigit() else 0
            go_strategy = Strategy.go_all if (go_value == 100 and use_percent) else Strategy.go_some
            diamond_strategy = Strategy.diamond_all if (diamond_value == 100 and use_percent) else Strategy.diamond_some
            rare_fur_strategy = Strategy.furs_some
            use_rares = values["furs"] if not window["furs"].Disabled else False

            if _is_female_enabled(window, female_value):
              print("modding females")
              _mod(reserve_key, species, Strategy.females, window, female_value, False, use_percent)
              window["male_value"].update("0")                
            if _is_male_enabled(window, male_value):
              print("modding males")
              _mod(reserve_key, species, Strategy.males, window, male_value, False, use_percent)
              window["male_value"].update("0")                                 
            if _is_go_enabled(window, go_value):
              print("modding go")
              _mod(reserve_key, species, go_strategy, window, go_value, use_rares, use_percent)        
            if _is_diamond_enabled(window, diamond_value):
              print("modding diamonds")
              _mod(reserve_key, species, diamond_strategy, window, diamond_value, use_rares, use_percent)   
            if _is_furs_enabled(window, rare_fur_value):
              print("modding rare furs")
              _mod(reserve_key, species, rare_fur_strategy, window, rare_fur_value, True, use_percent)                                  
            _disable_new_reserve(window)
          elif event == "great_ones":
            _mod(reserve_key, species, Strategy.go_furs, window, 0, True, False)             
          elif event == "diamonds":
            _mod(reserve_key, species, Strategy.diamond_furs, window, 0, True, False)   
          elif event == "others":
            _mod(reserve_key, species, Strategy.furs, window, 0, True, False)               
          elif event == "load_modded":
            window["modded_reserves"].update(values["load_modded"])  
          elif event == "list_mods":
            mods = _process_list_mods(window, reserve_name)
          elif event == "load_mod":
            confirm = sg.PopupOKCancel(f"{config.CONFIRM_LOAD_MOD} \n\n{config.BACKUP_WILL_BE_MADE}\n", title=config.CONFIRMATION, icon=logo.value, font=DEFAULT_FONT)
            if confirm == "OK":
              _load_mod(window, selected_mod[2])
              mods = _process_list_mods(window)
          elif event == "unload_mod":
            _unload_mod(window, selected_mod[2])
            mods = _process_list_mods(window)
          elif event == "reset":
            window["male_value"].update("0")
            window["female_value"].update("0")
            window["go_value"].update("0")
            window["diamond_value"].update("0")
            window["rare_fur_value"].update("0")
            window["by_percentage"].update(False)
            window["furs"].update(False)
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
            _value, key = event.split("::")
            if key == "update_translations":
              subprocess.Popen(f"pybabel compile --domain=apc --directory={config.APP_DIR_PATH / 'locale'}", shell=True)
        except Exception:
          _show_error_window(traceback.format_exc())
    
    window.close()

if __name__ == "__main__":
    main()