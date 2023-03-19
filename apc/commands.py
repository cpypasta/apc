from apc import adf, populations, utils, config
from rich.table import Table
from pathlib import Path

def _highlight_highs(reserve_description: list):
  diamond_row = 6
  go_row = 7
  for row in reserve_description:
    diamond_cnt = row[diamond_row]
    go_cnt = row[go_row]
    if diamond_cnt > 0:
      row[diamond_row] = f"[bold yellow]{diamond_cnt}[/bold yellow]"
    if go_cnt > 0:
      row[go_row] = f":boom: [bold red]{go_cnt}[/bold red]"

def _create_reserve_table(reserve_name: str, reserve_description: list, modded: bool = False) -> Table:
  reserve_name = config.get_reserve_name(reserve_name)
  title = f"[green]{reserve_name} Summary[/green]"
  table = Table(
    title=f"{title} [yellow](modded)[/yellow]" if modded else title, 
    row_styles=["dim", ""]
  )
  table.add_column("Species")
  table.add_column("Animals", justify="right")
  table.add_column("Males", justify="right")
  table.add_column("Females", justify="right")
  table.add_column("High Weight", justify="right")
  table.add_column("High Score", justify="right")
  table.add_column("Diamonds", justify="right")
  table.add_column("Great Ones", justify="right")
  _highlight_highs(reserve_description)
  return utils.list_to_table(reserve_description, table)  

def reserves() -> Table:
  reserve_names = [[reserve_name] for reserve_name in populations.reserves(True)]
  table = Table(
    title=f"[green]Reserves[/green]", 
    row_styles=["dim", ""]
  )
  table.add_column("Reserve Name (key)")

  return utils.list_to_table(reserve_names, table)

def species(reserve_name: str) -> Table:
  species = [[species_name] for species_name in populations.species(reserve_name, True)]
  table = Table(
    title=f"[green]{config.get_reserve_name(reserve_name)} Species[/green]", 
    row_styles=["dim", ""]
  )
  table.add_column("Species (key)")

  return utils.list_to_table(species, table)

def describe_reserve(reserve_name: str, modded: bool, include_species = True, verbose = False) -> Table:
  reserve_details = adf.load_reserve(reserve_name, modded, verbose=verbose)
  reserve_description = populations.describe_reserve(reserve_name, reserve_details.adf, include_species, verbose=verbose)
  return _create_reserve_table(reserve_name, reserve_description, modded)

def mod(reserve_name: str, species: str, strategy: str, modifier: int = None, modded: bool = False, verbose = False) -> Table:
  reserve_details = adf.load_reserve(reserve_name, modded, verbose=verbose)
  reserve_description = populations.mod(reserve_name, reserve_details, species, strategy, modifier, verbose=verbose)
  return _create_reserve_table(reserve_name, reserve_description, True)

def parse(filename: str, verbose = False) -> None:
  adf.load_adf(Path(filename), verbose)