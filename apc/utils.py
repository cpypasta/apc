import struct
import json
from rich.table import Table
from pathlib import Path
from apc import populations, adf, config
from typing import List

def list_to_table(
    data: list,
    table: Table,
) -> Table:
    for row in data:
        row = [str(x) for x in row]
        table.add_row(*row)

    return table

def update_uint(data_bytes: bytearray, offset: int, new_value: int) -> None:
    value_bytes = new_value.to_bytes(4, byteorder='little')
    for i in range(0, len(value_bytes)):
        data_bytes[offset + i] = value_bytes[i]

def update_float(data_bytes: bytearray, offset: int, new_value: float) -> None:
    hex_float = struct.pack("f", new_value)
    for i in range(0, 4):
        data_bytes[offset + i] = hex_float[i]

def format_key(key: str) -> str:
  key = [s.capitalize() for s in key.split("_")]
  return " ".join(key)

# TODO: all people calling this should stop and call config
def unformat_key(value: str) -> str:
  parts = value.lower().split(" ")
  return "_".join(parts)

def extract_animal_names(path: Path) -> dict:
  data = json.load(path.open())
  names = {}
  for animal in data.keys():
    names[animal] = { "animal_name": format_key(animal) }
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
  
def bad_scores(path: Path) -> None:
  data = json.load(path.open())
  for animal_key in data.keys():
    animal = data[animal_key]
    if animal["diamonds"]["score_low"] > animal["diamonds"]["score_high"]:
      print(animal_key, animal)
      
def seed_animals() -> None:
  reserve_name = "vurhonga"
  species = "sidestriped_jackal"
  seed = 6000  
  reserve = adf.load_reserve(reserve_name, True, False)
  while True:    
    species_details = populations._species(reserve_name, reserve.adf, species)
    groups = species_details.value["Groups"].value  
    start_seed = seed
    seed = populations.diamond_test_seed(species, groups, reserve.decompressed.data, seed)
    reserve.decompressed.save(config.MOD_DIR_PATH, False)
    entered = input(f"[{start_seed} to {seed}] press any key to continue; q to quit: ")
    if entered == "q":
      break

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

if __name__ == "__main__":
  # names = extract_animal_names(Path().cwd() / "config/animal_details.json")
  # Path(Path().cwd() / "config/animal_names.json").write_text(json.dumps(names, indent=2))  
  # names = extract_reserve_names(Path().cwd() / "config/reserve_details.json")
  # Path(Path().cwd() / "config/reserve_names.json").write_text(json.dumps(names, indent=2))
  # bad_scores(Path().cwd() / "config/animal_details.json")
  # seed_animals()
  # calc_seed([24930,37350,33,33,37350])
  calc_seed([25000,100,74700,100,100])