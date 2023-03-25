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
    is_diamond = True if row[diamond_col] == config.YES else False
    is_go = True if row[go_col] == config.YES else False
    if is_go > 0:
      row[go_col] = f":boom: [bold red]{config.YES}[/bold red]"
      row[diamond_col] = "-"
    elif is_diamond:
      row[diamond_col] = f"[bold yellow]{config.YES}[/bold yellow]"
      
def _create_reserve_table(reserve_name: str, reserve_description: list, modded: bool = False) -> Table:
  reserve_name = config.get_reserve_name(reserve_name)
  title = f"[green]{reserve_name} {config.SUMMARY}[/green]"
  table = Table(
    title=f"{title} [yellow]({config.MODDED})[/yellow]" if modded else title, 
    row_styles=["dim", ""]
  )
  table.add_column(config.SPECIES)
  table.add_column(config.ANIMALS_TITLE, justify="right")
  table.add_column(config.MALES, justify="right")
  table.add_column(config.FEMALES, justify="right")
  table.add_column(config.HIGH_WEIGHT, justify="right")
  table.add_column(config.HIGH_SCORE, justify="right")
  table.add_column(config.DIAMOND, justify="right")
  table.add_column(config.GREATONE, justify="right")
  _highlight_reserve_highs(reserve_description)
  return utils.list_to_table(reserve_description, table)  

def _create_animals_table(species: str, species_description: list, reserve_name: str = None, modded: bool = False) -> Table:
  species_name = config.get_species_name(species)
  if reserve_name:
    reserve_name = config.get_reserve_name(reserve_name)
    title = f"[green]{species_name} @ {reserve_name}[/green]"
  else:
    title = f"[green]{species_name}[/green]"
  table = Table(
    title=f"{title} [yellow](modded)[/yellow]" if modded else title, 
    row_styles=["dim", ""]
  )
  table.add_column(config.RESERVE)
  table.add_column(config.LEVEL,  justify="right")
  table.add_column(config.GENDER)
  table.add_column(config.WEIGHT, justify="right")
  table.add_column(config.SCORE, justify="right")
  table.add_column(config.VISUALSEED, justify="right")
  table.add_column(config.FUR)
  table.add_column(config.DIAMOND)
  table.add_column(config.GREATONE)
  _highlight_animal_highs(species_description)
  return utils.list_to_table(species_description, table)  

def reserves() -> Table:
  reserve_names = [[reserve_name] for reserve_name in populations.reserves(True)]
  table = Table(
    title=f"[green]{config.RESERVES_TITLE}[/green]", 
    row_styles=["dim", ""]
  )
  table.add_column(config.RESERVE_NAME_KEY)

  return utils.list_to_table(reserve_names, table)

def species(reserve_name: str) -> Table:
  species = [[species_name] for species_name in populations.species(reserve_name, True)]
  table = Table(
    title=f"[green]{config.get_reserve_name(reserve_name)} {config.SPECIES}[/green]", 
    row_styles=["dim", ""]
  )
  table.add_column(config.SPECIES_NAME_KEY)

  return utils.list_to_table(species, table)

def describe_reserve(reserve_name: str, modded: bool, include_species = True, verbose = False) -> Table:
  reserve_details = adf.load_reserve(reserve_name, modded, verbose=verbose)
  reserve_description = populations.describe_reserve(reserve_name, reserve_details.adf, include_species, verbose=verbose)
  return _create_reserve_table(reserve_name, reserve_description, modded)

def describe_animals(reserve_name: str, species: str, good: bool = False, modded: bool = False, verbose = False) -> Table:
  reserve_details = adf.load_reserve(reserve_name, modded, verbose=verbose)
  species_description = populations.describe_animals(reserve_name, species, reserve_details.adf, good, verbose=verbose)
  return _create_animals_table(species, species_description, reserve_name=reserve_name, modded=modded)

def find_animals(species: str, good: bool = False, modded: bool = False, verbose = False) -> Table:
  species_description = populations.find_animals(species, good=good, modded=modded, verbose=verbose)
  return _create_animals_table(species, species_description, modded=modded)

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