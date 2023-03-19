import PySimpleGUI as sg
import os
from apc import populations, adf
from pathlib import Path
from apcgui import __version__

DEFAULT_FONT = "_ 16"

RESERVE_COLUMNS = [
    "Species",
    "Groups",
    "Animals",
    "Males",
    "Females",
    "High Weight",
    "High Score",
    "Great Ones"
]

def _app_path() -> Path:
   return Path(os.path.realpath(__file__)).parents[0]

def reserves() -> list:
    return populations.reserves()

def main():
    reserve_names = reserves()

    sg.theme("DarkAmber")
    layout = [
        [sg.Image(str(_app_path() / "images/logo.png")), sg.T('Animal Population Changer', justification='l', expand_x=True, font="_ 24"), sg.T(f"Version: {__version__}", justification="r", font="_ 12", expand_y=False)],
        [sg.T("Hunting Reserve:"), sg.Combo(reserve_names, default_value="layton", s=(15,len(reserve_names)), k="reserve_name"), sg.Button("Load")],
        [sg.Table([], RESERVE_COLUMNS, num_rows=18, expand_x=True, k="reserve_details")]
    ]

    window = sg.Window('Animal Population Changer', layout, resizable=True, font=DEFAULT_FONT)

    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED:
            break 
        if event == "Load":
            reserve_name = values["reserve_name"]
            reserve_details = populations.describe_reserve(reserve_name, adf.load_reserve(reserve_name).adf)
            window["reserve_details"].update(reserve_details)
            
    
    window.close()

if __name__ == "__main__":
    main()