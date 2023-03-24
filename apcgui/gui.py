import PySimpleGUI as sg
import time
from apc import populations, adf
from apc.config import valid_go_species, Strategy, MOD_DIR_PATH, save_path, get_save_path
from apcgui import __version__, logo
from apc.utils import unformat_key, format_key

DEFAULT_FONT = "_ 14"
MEDIUM_FONT = "_ 13"
SMALL_FONT = "_ 11"
PROGRESS_DELAY = 0.5
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
  window["diamond_percent"].update(disabled = disabled)  

def _disable_go(window: sg.Window, disabled: bool) -> None:
  window["great_ones"].update(disabled = disabled)  
  window["go_percent"].update(disabled = disabled)

def _reserve_key_from_name(name: str) -> str:
  return reserve_keys[reserve_names.index(name)]   

def _show_species_description(window: sg.Window, species_name: str) -> None:
    window["reserve_description"].update(visible=False)
    window["modding"].update(visible=False)
    window["species_description"].update(visible=True)
    window["show_reserve"].update(visible=True)
    window["species_name"].update(f"** {species_name.upper()} **")
    window["show_species_group"].update(visible=False)

def _show_reserve_description(window: sg.Window) -> None:
    window["reserve_description"].update(visible=True)
    window["modding"].update(visible=True)
    window["species_description"].update(visible=False)
    window["show_reserve"].update(visible=False)
    window["species_name"].update("")
    window["show_species_group"].update(visible=True)    

def _viewing_modded(window: sg.Window) -> bool:
  return window['reserve_warning'].get() == VIEW_MODDED  

def _is_diamond_enabled(window: sg.Window) -> bool:
  return not window["diamonds"].Disabled

def _is_go_enabled(window: sg.Window) -> bool:
  return not window["great_ones"].Disabled

def _show_error(window: sg.Window, ex: adf.FileNotFound) -> None:
  window["progress"].update(visible=False)
  window["progress"].update(0)      
  window["reserve_note"].update(f"Error: {ex}")          

def _mod(reserve_key: str, species: str, strategy: Strategy, window: sg.Window, modifier: int, rares: bool) -> None:
  window["progress"].update(visible=True)
  print((reserve_key, species, strategy.value, modifier, rares))
  is_modded = _viewing_modded(window)
  try:
    reserve_details = adf.load_reserve(reserve_key, mod=is_modded)
  except adf.FileNotFound as ex:
    _show_error(window, ex)
    return
  window["progress"].update(25)
  try:
    modded_reserve_description = populations.mod(reserve_key, reserve_details, species, strategy.value, rares=rares, modifier=modifier)
  except Exception as ex:
    _show_error(window, ex)
    return
  window["progress"].update(50)
  window["reserve_description"].update(_highlight_values(modded_reserve_description))
  window["progress"].update(75)
  window["reserve_warning"].update(VIEW_MODDED)
  window["reserve_note"].update(f"{format_key(species).upper()} mod has been saved to: \"{MOD_DIR_PATH}\"")
  window["progress"].update(100)
  time.sleep(PROGRESS_DELAY)
  window["progress"].update(visible=False)
  window["progress"].update(0)
  _disable_diamonds(window, True)
  _disable_go(window, True)
  window["update_percent"].update(disabled=True)

def main():
    sg.theme("DarkAmber")

    mod_layout = [
        [sg.Column([
          [sg.T("Great Ones:", font=MEDIUM_FONT, expand_x=True), sg.Input(s=4, default_text="100", disabled=True, k="go_percent")],
          [sg.T("Diamonds:", font=MEDIUM_FONT, expand_x=True), sg.Input(s=4, default_text="100", disabled=True, k="diamond_percent")]
        ], expand_x=True)],        
        [sg.Checkbox("include rare furs", k="furs")],
        [sg.Button("Update", expand_x=True, disabled=True, k="update_percent")]        
    ]

    layout = [
        [
          sg.Image(logo.value), 
          sg.Column([
            [sg.T('Animal Population Changer', expand_x=True, font="_ 24")],
            [sg.T(save_path_value, font=SMALL_FONT, k="save_path")]
          ]), 
          sg.Push(),
          sg.T(f"version: {__version__}", font=SMALL_FONT, p=((0,0),(0,60)))
        ],
        [
          sg.Column([[sg.T("Hunting Reserve:"), 
                      sg.Combo(reserve_names, s=(reserve_name_size,len(reserve_names)), k="reserve_name", enable_events=True, metadata=reserve_keys)
                    ]], p=((0, 0), (10, 10))),
          sg.Column([[sg.Button("configure path",k="set_save", font=SMALL_FONT),
          sg.Column([[sg.Button("show animals", k="show_species", font=SMALL_FONT), sg.Checkbox("only good ones", k="good_ones")]], k="show_species_group", visible=False),
          sg.Button("show reserve", k="show_reserve", font=SMALL_FONT, visible=False)]]),
          sg.T("", text_color="orange", k="reserve_warning"),
          sg.T("", k="species_name"),
          sg.ProgressBar(100, orientation='h', expand_x=True, size=(20, 20),  key='progress', visible=False)
        ],
        [sg.Table(
            [], 
            RESERVE_COLUMNS, 
            num_rows=19, 
            expand_x=True, 
            k="reserve_description", 
            font=MEDIUM_FONT, 
            hide_vertical_scroll=True,
            col_widths=[15,7,5,7,11,10,8,10],
            auto_size_columns=False,
            header_background_color="brown",
            enable_click_events=True
          ), sg.Table(
            [], 
            SPECIES_COLUMNS, 
            num_rows=19, 
            expand_x=True, 
            k="species_description", 
            font=MEDIUM_FONT, 
            header_background_color="brown",
            visible=False
          ),        
          sg.Column([  
            [sg.Frame("Percent Modding", mod_layout)],
            [sg.Frame("Unique Furs", [
              [sg.Button("Great Ones", expand_x=True, disabled=True, k="great_ones")],
              [sg.Button("Diamonds", expand_x=True, disabled=True, k="diamonds")]
            ], expand_x=True)]
          ], k="modding", vertical_alignment="top")
        ],
        [
          sg.T("", text_color="orange", k="reserve_note")
        ]
    ]

    window = sg.Window('Animal Population Changer', layout, resizable=True, font=DEFAULT_FONT, icon=logo.value, size=(1200, 590))
    reserve_details = None

    while True:
        event, values = window.read()
        print(event, values)

        if event == sg.WIN_CLOSED:
            break 
        
        window["show_species_group"].update(visible=False)
        window["show_reserve"].update(visible=False)

        reserve_name = values["reserve_name"] if "reserve_name" in values else None
        if event == "reserve_name" and reserve_name:
          window["reserve_warning"].update("")
          window["reserve_note"].update("")   
          window["progress"].update(visible=True)
          reserve_key = _reserve_key_from_name(reserve_name)
          try:
            reserve_details = adf.load_reserve(reserve_key)
            window["progress"].update(50)            
          except adf.FileNotFound as ex:
            _show_error(window, ex)    
            continue
          reserve_description = populations.describe_reserve(reserve_key, reserve_details.adf)
          window["progress"].update(90)
          window["reserve_description"].update(_highlight_values(reserve_description))
          window["progress"].update(100)
          time.sleep(PROGRESS_DELAY)
          window["progress"].update(visible=False)
          window["progress"].update(0)
        elif isinstance(event, tuple):
          if event[0] == "reserve_description" and event[1] == "+CLICKED+" and reserve_name:
            row, _ = event[2]
            if row != None and row >= 0:
              window["update_percent"].update(disabled=False)
              species_name = reserve_description[row][0] if reserve_description else ""
              species = unformat_key(species_name)
              print(f"species clicked: {species}")
              window["show_species_group"].update(visible=True)
              _disable_diamonds(window, True)
              _disable_go(window, True)
              window["reserve_note"].update("")
              _disable_diamonds(window, False)
              if valid_go_species(species):
                _disable_go(window, False)
        elif event == "set_save":
          provided_path = sg.popup_get_folder("Select the folder where the game saves your files:", title="Saves Path")
          if provided_path:
            save_path(provided_path)
            window["save_path"].update(provided_path)
            window["reserve_note"].update(f"Game path saved")
        elif event == "show_species":
          print((reserve_key, species))                  
          window["progress"].update(visible=True)
          is_modded = _viewing_modded(window)
          try:
            reserve_details = adf.load_reserve(reserve_key, mod=is_modded)
          except adf.FileNotFound as ex:
            _show_error(window, ex)
            continue
          window["progress"].update(30)
          species_description = populations.describe_animals(reserve_key, species, reserve_details.adf, good=values["good_ones"])
          window["progress"].update(60)
          window["species_description"].update(species_description)
          window["progress"].update(100)
          _show_species_description(window, species_name)           
          time.sleep(PROGRESS_DELAY)
          window["progress"].update(visible=False)
          window["progress"].update(0)
        elif event == "show_reserve":
          _show_reserve_description(window)
          window["show_species_group"].update(visible=False)
        elif event == "update_percent":
          use_rares = values["furs"]
          go_percent = int(values["go_percent"])
          diamond_percent = int(values["diamond_percent"])   
          go_strategy = Strategy.go_all if go_percent == 100 else Strategy.go_some
          diamond_strategy = Strategy.diamond_all if diamond_percent == 100 else Strategy.diamond_some
                 
          if _is_diamond_enabled(window) and _is_go_enabled(window):            
            _mod(reserve_key, species, go_strategy, window, go_percent, use_rares)
            _mod(reserve_key, species, diamond_strategy, window, diamond_percent, use_rares)        
          elif _is_diamond_enabled(window):
            _mod(reserve_key, species, diamond_strategy, window, diamond_percent, use_rares)        
          elif _is_go_enabled(window):
            _mod(reserve_key, species, go_strategy, window, go_percent, use_rares)        
          else:
            print("neither dimaond or go is enabled")
        elif event == "great_ones":
          _mod(reserve_key, species, Strategy.go_furs, window, 0, True)             
        elif event == "diamonds":
          _mod(reserve_key, species, Strategy.diamond_furs, window, 0, True)     
            
    
    window.close()

if __name__ == "__main__":
    main()