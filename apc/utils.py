import struct
from rich.table import Table

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

def unformat_key(value: str) -> str:
  """do not use in production code"""
  parts = value.lower().split(" ")
  return "_".join(parts)