import PySimpleGUI as sg
import time
from apc import populations, adf
from apc.config import valid_go_species, valid_species_to_modify, Strategy, MOD_DIR_PATH
from apcgui import __version__, logo
from apc.utils import unformat_key

DEFAULT_FONT = "_ 14"
BUTTON_FONT = "_13"

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

reserve_keys = populations.reserve_keys()
reserve_names = populations.reserves()
reserve_name_size = len(max(reserve_names, key = len))

def _disable_diamonds(window: sg.Window, disabled: bool) -> None:
  window["all_diamonds"].update(disabled = disabled)
  window["some_diamonds"].update(disabled = disabled)    

def _disable_go(window: sg.Window, disabled: bool) -> None:
  window["all_go"].update(disabled = disabled)
  window["some_go"].update(disabled = disabled)    
  window["go_furs"].update(disabled = disabled)    

def _reserve_key_from_name(name: str) -> str:
  return reserve_keys[reserve_names.index(name)]   

def _mod(reserve_key: str, species: str, strategy: Strategy, window: sg.Window, values: dict, modifier: int) -> None:
  window["progress"].update(visible=True)
  rares = values["furs"]
  print((reserve_key, species, strategy.value))
  reserve_details = adf.load_reserve(reserve_key, mod=values["modded"])
  window["progress"].update(25)
  modded_reserve_description = populations.mod(reserve_key, reserve_details, species, strategy.value, rares=rares, modifier=modifier)
  window["progress"].update(50)
  window["reserve_description"].update(modded_reserve_description)
  window["progress"].update(75)
  window["reserve_warning"].update("(modded)")
  window["reserve_note"].update(f"Mod saved to: \"{MOD_DIR_PATH}\"")
  window["progress"].update(100)
  time.sleep(1)
  window["progress"].update(visible=False)
  window["progress"].update(0)

def main():
    sg.theme("DarkAmber")

    mod_layout = [
        [sg.Button("All GOs", disabled=True, k="all_go", font=BUTTON_FONT)],
        [sg.Button("All GO Furs", disabled=True, k="go_furs", font=BUTTON_FONT)],
        [sg.Button("Some GOs", disabled=True, k="some_go", font=BUTTON_FONT), sg.Input(s=2, default_text="50", k="go_percent")],
        [sg.Button("All Diamonds", disabled=True, k="all_diamonds", font=BUTTON_FONT)],
        [sg.Button("Some Diamonds", disabled=True, k="some_diamonds", font=BUTTON_FONT), sg.Input(s=2, default_text="50", k="diamond_percent")],

        [sg.Frame("options", [
          [sg.Checkbox('used modded', k="modded")],
          [sg.Checkbox("include rare furs", k="furs")]
        ], expand_x=True)]        
    ]

    layout = [
        [
          sg.Image(logo.value), 
          sg.T('Animal Population Changer', expand_x=True, font="_ 24"), 
          sg.T(f"version: {__version__}", font="_ 12", p=((0,0),(0,60)))
        ],
        [
          sg.Column([[sg.T("Hunting Reserve:"), 
                      sg.Combo(reserve_names, s=(reserve_name_size,len(reserve_names)), k="reserve_name", enable_events=True, metadata=reserve_keys)
                    ]], p=((0, 0), (10, 10))),
          sg.T("", text_color="orange", k="reserve_warning"),
          sg.ProgressBar(100, orientation='h', expand_x=True, size=(20, 20),  key='progress', visible=False), sg.T("", key="progress_x")
        ],
        [sg.Table(
            [], 
            RESERVE_COLUMNS, 
            num_rows=19, 
            expand_x=True, 
            k="reserve_description", 
            font="_ 13", 
            hide_vertical_scroll=True,
            col_widths=[15,7,5,7,11,10,8,10],
            auto_size_columns=False,
            alternating_row_color=sg.theme_input_background_color(),
            header_background_color="brown",
            enable_click_events=True
          ), 
          sg.Frame("Modding", mod_layout, vertical_alignment="top"),
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
        
        reserve_name = values["reserve_name"] if "reserve_name" in values else None
        if event == "reserve_name" and reserve_name:
          window["progress"].update(visible=True)
          reserve_key = _reserve_key_from_name(reserve_name)
          reserve_details = adf.load_reserve(reserve_key)
          window["progress"].update(50)
          reserve_description = populations.describe_reserve(reserve_key, reserve_details.adf)
          window["progress"].update(90)
          window["reserve_description"].update(reserve_description)
          window["progress"].update(100)
          time.sleep(1)
          window["progress"].update(visible=False)
          window["progress"].update(0)
        elif isinstance(event, tuple):
          if event[0] == "reserve_description" and event[1] == "+CLICKED+" and reserve_name:
            row, _ = event[2]
            if row and row >= 0:
              species = unformat_key(reserve_description[row][0]) if reserve_description else ""
              _disable_diamonds(window, True)
              _disable_go(window, True)
              if valid_species_to_modify(species):
                  window["reserve_note"].update("")
                  _disable_diamonds(window, False)
                  if valid_go_species(species):
                    _disable_go(window, False)
              else:
                window["reserve_note"].update("*species not mod enabled")
        elif event == "all_go":
          _mod(reserve_key, species, Strategy.go_all, window, values, 0)        
        elif event == "go_furs":
          _mod(reserve_key, species, Strategy.go_furs, window, values, 0)             
        elif event == "some_go":
          _mod(reserve_key, species, Strategy.go_some, window, values, int(values["go_percent"]))        
        elif event == "all_diamonds":
          _mod(reserve_key, species, Strategy.diamond_all, window, values, 0)        
        elif event == "some_diamonds":
          _mod(reserve_key, species, Strategy.diamond_some, window, values, int(values["diamond_percent"]))
            
    
    window.close()

if __name__ == "__main__":
    main()