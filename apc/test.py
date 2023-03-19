import os
import sys
from pathlib import Path
import re

# C:\Users\appma\Documents\Avalanche Studios\COTW\Saves\76561198332334673
saves = Path().home() / "Documents/Avalanche Studios/COTW/Saves"

# if saves.exists:
#   folders = os.listdir(saves)
#   all_numbers = re.compile(r"\d+")
#   for folder in folders:
#       if all_numbers.match(folder):
#          print(f"this matches {folder}")

print(saves.exists())
print(saves)
print(os.listdir(saves))