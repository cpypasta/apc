import PySimpleGUI as sg
import sys, traceback, time, os, re, shutil
from apc import populations, adf
from apc.config import valid_go_species, Strategy, MOD_DIR_PATH, save_path, get_save_path, get_population_file_name, get_reserve_species_key, get_population_name, BACKUP_DIR_PATH
from apcgui import __version__, logo, tgui, use_languages
from apc.utils import format_key
from typing import List
from pathlib import Path

translate = tgui.gettext

DEFAULT_FONT = "_ 14"
MEDIUM_FONT = "_ 13"
SMALL_FONT = "_ 11"
PROGRESS_DELAY = 0.3
VIEW_MODDED="(viewing modded)"

RESERVE_COLUMNS = [
    "Species", 
    "Animals",
    "Males",
    "Females",
    "High Weight",
    "High Score", 
    "Diamonds", 
    "Great Ones" 
]
SPECIES_COLUMNS = [
  "Reserve",
  "Level",
  "Gender",
  "Weight",
  "Score",
  "Visual Seed",
  "Fur",
  "Diamond",
  "Great One"
]

reserve_keys = populations.reserve_keys()
reserve_names = populations.reserves()
reserve_name_size = len(max(reserve_names, key = len))
save_path_value = get_save_path()

def _progress(window: sg.Window, value: int) -> None:
 window["progress"].update(int)   

def _show_error_window(error):
  layout = [
    [sg.T("Please copy and paste as a new bug on Nexusmods here:")],
    [sg.Multiline("https://www.nexusmods.com/thehuntercallofthewild/mods/225?tab=bugs", expand_x=True, no_scrollbar=True, disabled=True)],
    [sg.T("ERROR:")],
    [sg.Multiline(error, expand_x=True, expand_y=True, disabled=True)]
  ]
  window = sg.Window("Unexpected Error", layout, modal=True, size=(600, 300), icon=logo.value)
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
  window["diamonds"].update(disabled = disabled)  
  window["others"].update(disabled = disabled)    
  window["diamond_value"].update(disabled = disabled)
  window["male_value"].update(disabled = disabled)
  window["female_value"].update(disabled = disabled)
  window["rare_fur_value"].update(disabled = disabled)

def _disable_go(window: sg.Window, disabled: bool) -> None:
  window["great_ones"].update(disabled = disabled)  
  window["go_value"].update(disabled = disabled)

def _disable_new_reserve(window: sg.Window) -> None:
  _disable_diamonds(window, True)
  _disable_go(window, True)  
  window["show_animals"].update(disabled=True)
  window["update_animals"].update(disabled=True)

def _reserve_key_from_name(name: str) -> str:
  return reserve_keys[reserve_names.index(name)]  # TODO: won't work when translations come

def _show_species_description(window: sg.Window, species_name: str) -> None:
    window["reserve_description"].update(visible=False)
    window["modding"].update(visible=False)
    window["species_description"].update(visible=True)
    window["show_reserve"].update(visible=True)
    window["species_name"].update(f"{species_name.upper()}")
    window["mod_list"].update(visible=False)

def _show_reserve_description(window: sg.Window) -> None:
    window["reserve_description"].update(visible=True)
    window["modding"].update(visible=True)
    window["species_description"].update(visible=False)
    window["show_reserve"].update(visible=False)
    window["species_name"].update("")
    window["discover_warning"].update(visible=False)
    window['reserve_warning'].update(visible=True)   
    window["mod_list"].update(visible=False) 
    window["mod_tab"].update(disabled=False)
    window["mod_tab"].select()
    window["explore_tab"].update(disabled=False)    
    window["reserve_note"].update("")
    window["load_mod"].update(disabled=True)
    window["unload_mod"].update(disabled=True)    

def _show_mod_list(window: sg.Window) -> None:
  window["reserve_description"].update(visible=False)
  window["mod_list"].update(visible=True)
  window["show_reserve"].update(visible=True)
  window["mod_tab"].update(disabled=True)
  window["explore_tab"].update(disabled=True)
  window["load_mod"].update(disabled=True)
  window["unload_mod"].update(disabled=True)
  

def _viewing_modded(window: sg.Window) -> bool:
  return window['reserve_warning'].get() == VIEW_MODDED  

def _is_male_enabled(window: sg.Window, value: int) -> bool:
  return not window["male_value"].Disabled and value != 0 

def _is_female_enabled(window: sg.Window, value: int) -> bool:
  return not window["female_value"].Disabled and value != 0 

def _is_furs_enabled(window: sg.Window, value: int) -> bool:
  return _is_diamond_enabled(window, value)

def _is_diamond_enabled(window: sg.Window, value: int) -> bool:
  print(window["diamonds"].Disabled, value)
  return not window["diamonds"].Disabled and value != 0

def _is_go_enabled(window: sg.Window, value: int) -> bool:
  return not window["great_ones"].Disabled and value != 0

def _show_error(window: sg.Window, ex: adf.FileNotFound) -> None:
  window["progress"].update(0)      
  window["reserve_note"].update(f"Error: {ex}")      
  print("ERROR", traceback.print_exc(file=sys.stdout))   
   
def _show_warning(window: sg.Window, message: str) -> None:
  window["progress"].update(0)      
  window["reserve_note"].update(f"Warning: {message}")

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
  window["reserve_note"].update(f"{format_key(species).upper()} ({strategy}) Saved: \"{MOD_DIR_PATH / get_population_file_name(reserve_key)}\"")
  window["progress"].update(100)
  time.sleep(PROGRESS_DELAY)
  window["progress"].update(0)  
  window["show_animals"].update(disabled=True)
  window["update_animals"].update(disabled=True)

def _list_mods(window: sg.Window) -> List[List[str]]:
  if not MOD_DIR_PATH.exists():
    return _show_warning(window, f"{MOD_DIR_PATH} does not exist.")
  
  file_format = re.compile(r"^.*animal_population_\d+$")
  items = os.scandir(MOD_DIR_PATH)
  mods = []
  for item in items:
    item_path = MOD_DIR_PATH / item.name
    if item.is_file() and file_format.match(item.name):
      already_loaded = (BACKUP_DIR_PATH / item.name).exists()
      already_loaded = "Yes" if already_loaded else "-"
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
          _show_warning(window, f"failed to backup game {game_file}")
          return
    else:
      print("backup already exists")
    _progress(window, 50)
    game_path = _copy_file(filename, get_save_path())
    if not game_path:
      _show_warning(window, f"failed to load mod {filename}")
      return    
    _progress(window, 100)
    sg.PopupOK("Mod has been loaded", font=DEFAULT_FONT, icon=logo.value, title="Mod Loaded")
    time.sleep(PROGRESS_DELAY)
  except Exception:
    print(traceback.format_exc())
    _show_warning(window, "failed to load mod")    
  _progress(window, 0)

def _unload_mod(window: sg.Window, filename: Path) -> None:
  window["reserve_note"].update("")
  try:
    backup_file = BACKUP_DIR_PATH / filename.name
    game_path = get_save_path()
    if not backup_file.exists():
      _show_warning(window, f"{backup_file} does not exist")
      return
    game_path = _copy_file(backup_file, game_path)    
    if not game_path:
      _show_warning(window, f"failed to load backup file to {game_path}")
      return
    _progress(window, 50)
    os.remove(backup_file)
    _progress(window, 100)
    sg.PopupOK("Mod has been unloaded", font=DEFAULT_FONT, icon=logo.value, title="Mod Unloaded")
    time.sleep(PROGRESS_DELAY)
  except Exception:
    print(traceback.format_exc())
    _show_warning(window, f"failed to unload mod")    
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
            [sg.T(translate('Animal Population Changer'), expand_x=True, font="_ 24")],
            [sg.T(save_path_value, font=SMALL_FONT, k="save_path")],
            [sg.Column([
              [sg.Checkbox("use modded populations", k="load_modded", font=MEDIUM_FONT, enable_events=True), 
               sg.T("", text_color="orange", k="reserve_warning", font=MEDIUM_FONT)],
            ], p=(0,0))]
          ]), 
          sg.Push(),
          sg.T(f"version: {__version__} ({use_languages[0]})", font=SMALL_FONT, p=((0,0),(0,60)))
        ],
        [
          sg.Column([[sg.T("Hunting Reserve:"), 
                      sg.Combo(reserve_names, s=(reserve_name_size,len(reserve_names)), k="reserve_name", enable_events=True, metadata=reserve_keys)
                    ]], p=((0, 0), (10, 10))),          
          sg.Column([[sg.Button("back to reserve", k="show_reserve", font=SMALL_FONT, visible=False)]], p=(0,0)),
          sg.Column([[sg.T("", text_color="orange", k="reserve_warning", font=MEDIUM_FONT)]], p=(0,0)),
          sg.Column([[sg.T("", k="species_name", text_color="orange")]], p=(0,0)),
          sg.Column([[sg.T("(modded)", text_color="orange", k="discover_warning", visible=False, font=MEDIUM_FONT)]], p=(0,0))
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
              ["Reserve", "Loaded", "Modded File"],
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
              sg.Tab("Mod", [
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.Column([
                  [sg.T("Males:", font=DEFAULT_FONT, expand_x=True), sg.Input(s=4, default_text="0", k="male_value")],
                  [sg.T("Females:", font=DEFAULT_FONT, expand_x=True), sg.Input(s=4, default_text="0", k="female_value")],
                  [sg.T("Great Ones"+":", font=DEFAULT_FONT, expand_x=True), sg.Input(s=4, default_text="0", k="go_value")],
                  [sg.T("Diamonds:", font=DEFAULT_FONT, expand_x=True), sg.Input(s=4, default_text="0", k="diamond_value")],
                  [sg.T("Rare Furs:", font=DEFAULT_FONT, expand_x=True), sg.Input(s=4, default_text="0", k="rare_fur_value")]
                ] , expand_x=True)],
                [sg.Checkbox("include rare furs", k="furs", font=MEDIUM_FONT, tooltip="Will include rare furs if available")],
                [sg.Checkbox("update by percentage", k="by_percentage", font=MEDIUM_FONT, tooltip="Use numbers provided above as percentage of animals")],
                [sg.Button("Update Animals", expand_x=True, disabled=True, k="update_animals")],
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.T("Just the Furs:")],
                [sg.T("(one of each fur)", font=SMALL_FONT, p=(5,0))],
                [sg.Button("Great Ones", expand_x=True, disabled=True, k="great_ones")],
                [sg.Button("Diamonds", expand_x=True, disabled=True, k="diamonds")],
                [sg.Button("Others", expand_x=True, disabled=True, k="others")],
                [sg.T(" ", font="_ 3", p=(0,0))]
              ], k="mod_tab"),
              sg.Tab("Explore", [
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.Checkbox("diamonds and Great Ones", font=MEDIUM_FONT, default=True, k="good_ones")],
                [sg.Checkbox("top 10 scores", font=MEDIUM_FONT, k="top_scores")],
                [sg.Checkbox("look at all reserves", font=MEDIUM_FONT, k="all_reserves")],
                [sg.Checkbox("look at modded animals", font=MEDIUM_FONT, k="modded_reserves")],
                [sg.Button("Show Animals", expand_x=True, k="show_animals", disabled=True)]
              ], k="explore_tab"),
              sg.Tab("Files", [
                [sg.T(" ", font="_ 3", p=(0,0))],
                [sg.Button("Configure Game Path", expand_x=True, k="set_save")],
                [sg.Button("List Mods", expand_x=True, k="list_mods")],
                [sg.Button("Load Mod", expand_x=True, k="load_mod", disabled=True)],
                [sg.Button("Unload Mod", expand_x=True, k="unload_mod", disabled=True)],
              ])
            ]], p=(0,5))
          ]], vertical_alignment="top", p=(0,0), k="modding")         
        ],               
        [
          sg.T("", text_color="orange", k="reserve_note")
        ]
    ]

    window = sg.Window('Animal Population Changer', layout, resizable=True, font=DEFAULT_FONT, icon=logo.value, size=(1200, 750))
    reserve_details = None

    while True:
        event, values = window.read()
        # print(event, values)

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
              continue
            reserve_description = populations.describe_reserve(reserve_key, reserve_details.adf)
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
                species = get_reserve_species_key(species_name, reserve_key)
                print(f"species clicked: {species}")
                _disable_diamonds(window, True)
                _disable_go(window, True)
                window["reserve_note"].update("")
                _disable_diamonds(window, False)
                window["show_animals"].update(disabled=False)
                if valid_go_species(species):
                  _disable_go(window, False)
            elif event[0] == "mod_list" and event[1] == "+CLICKED+":
              row, _ = event[2]
              if row != None and row >= 0:
                selected_mod = mods[row]
                window["load_mod"].update(disabled=False)
                window["unload_mod"].update(disabled=selected_mod[1] != "Yes")                
          elif event == "set_save":
            provided_path = sg.popup_get_folder("Select the folder where the game saves your files:", title="Saves Path", icon=logo.value, font=DEFAULT_FONT)
            if provided_path:
              save_path(provided_path)
              window["save_path"].update(provided_path)
              window["reserve_note"].update(f"Game path saved")
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
            _show_species_description(window, species_name)
            if is_modded:
              window["discover_warning"].update(visible=True)           
            time.sleep(PROGRESS_DELAY)
            window["progress"].update(0)
          elif event == "show_reserve":
            _show_reserve_description(window)
          elif event == "update_animals":
            male_value = int(values["male_value"]) if values["male_value"].isdigit() else 0
            female_value = int(values["female_value"]) if values["female_value"].isdigit() else 0
            go_value = int(values["go_value"]) if values["go_value"].isdigit() else 0
            diamond_value = int(values["diamond_value"]) if values["diamond_value"].isdigit() else 0
            rare_fur_value = int(values["rare_fur_value"]) if values["rare_fur_value"].isdigit() else 0
            go_strategy = Strategy.go_all if (go_value == 100 and use_percent) else Strategy.go_some
            diamond_strategy = Strategy.diamond_all if (diamond_value == 100 and use_percent) else Strategy.diamond_some
            rare_fur_strategy = Strategy.furs_some
            use_rares = values["furs"]
            use_percent = values["by_percentage"]
            
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
            confirm = sg.PopupOKCancel(f"Are you sure you want to overwrite your {selected_mod[0]} game file with the modded one? \n\nDon't worry, a backup copy will be made.\n", title="Confirmation", icon=logo.value, font=DEFAULT_FONT)
            if confirm == "OK":
              _load_mod(window, selected_mod[2])
              mods = _process_list_mods(window)
          elif event == "unload_mod":
            _unload_mod(window, selected_mod[2])
            mods = _process_list_mods(window)
            
        except Exception:
          _show_error_window(traceback.format_exc())
    
    window.close()

if __name__ == "__main__":
    main()