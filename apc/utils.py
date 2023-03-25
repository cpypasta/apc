import struct
import json
from rich.table import Table
from pathlib import Path

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

if __name__ == "__main__":
  names = extract_animal_names(Path().cwd() / "config/animal_details.json")
  Path(Path().cwd() / "config/animal_names.json").write_text(json.dumps(names, indent=2))  
  names = extract_reserve_names(Path().cwd() / "config/reserve_details.json")
  Path(Path().cwd() / "config/reserve_names.json").write_text(json.dumps(names, indent=2))