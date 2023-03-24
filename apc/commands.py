from apc import adf, populations, utils, config
from rich.table import Table
from rich import print
from pathlib import Path

def _highlight_reserve_highs(reserve_description: list) -> None:
  diamond_col = 6
  go_col = 7
  for row in reserve_description:
    diamond_cnt = row[diamond_col]
    go_cnt = row[go_col]
    if diamond_cnt > 0:
      row[diamond_col] = f"[bold yellow]{diamond_cnt}[/bold yellow]"
    if go_cnt > 0:
      row[go_col] = f":boom: [bold red]{go_cnt}[/bold red]"

def _highlight_animal_highs(species_description: list) -> None:
  diamond_col = 5
  go_col = 6
  for row in species_description:
    is_diamond = True if row[diamond_col] == "yes" else False
    is_go = True if row[go_col] == "yes" else False
    if is_go > 0:
      row[go_col] = f":boom: [bold red]yes[/bold red]"
      row[diamond_col] = "-"
    elif is_diamond:
      row[diamond_col] = f"[bold yellow]yes[/bold yellow]"
      
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
  table.add_column("GOs", justify="right")
  _highlight_reserve_highs(reserve_description)
  return utils.list_to_table(reserve_description, table)  

def _create_animals_table(reserve_name: str, species: str, species_description: list, modded: bool = False) -> Table:
  reserve_name = config.get_reserve_name(reserve_name)
  species_name = utils.format_key(species)
  title = f"[green]{species_name} at {reserve_name}[/green]"
  table = Table(
    title=f"{title} [yellow](modded)[/yellow]" if modded else title, 
    row_styles=["dim", ""]
  )
  table.add_column("Level",  justify="right")
  table.add_column("Gender")
  table.add_column("Weight", justify="right")
  table.add_column("Score", justify="right")
  table.add_column("Visual Seed", justify="right")
  table.add_column("Fur")
  table.add_column("Diamond")
  table.add_column("GO")
  _highlight_animal_highs(species_description)
  return utils.list_to_table(species_description, table)  

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

def describe_animals(reserve_name: str, species: str, good: bool = False, modded: bool = False, verbose = False) -> Table:
  reserve_details = adf.load_reserve(reserve_name, modded, verbose=verbose)
  species_description = populations.describe_animals(reserve_name, species, reserve_details.adf, good, verbose=verbose)
  return _create_animals_table(reserve_name, species, species_description, modded)

def mod(reserve_name: str, species: str, strategy: str, modifier: int = None, rares: bool = False, modded: bool = False, verbose = False) -> Table:
  if verbose:
    if modded:
      print("[yellow]Using existing modded file to mod...[/yellow]")
    if rares:
      print("[yellow]Will use rare fur types when modding...[/yellow]")
  reserve_details = adf.load_reserve(reserve_name, modded, verbose=verbose)
  reserve_description = populations.mod(reserve_name, reserve_details, species, strategy, modifier, rares, verbose=verbose)
  return _create_reserve_table(reserve_name, reserve_description, True)

def parse(filename: str, verbose = False) -> None:
  adf.load_adf(Path(filename), verbose)