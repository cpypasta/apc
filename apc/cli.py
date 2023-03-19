from typing import Optional
from rich import print
from rich.console import Console
from apc import commands, config

import typer

from apc import __app_name__, __version__, config

app = typer.Typer()
console = Console()
state = { "verbose": False }

@app.command(name="set-save", help="Set the location of animal population files")
def set_save(save_path: str = typer.Argument(...)) -> None:
  config.save_path(save_path)
  print(f"[green]The save path {save_path} has been saved[/green]")

@app.command(name="show-save", help="Show the location of animal population files")
def show_save() -> None:
  save_path = config.get_save_path()
  print(f"[green]The save path is {save_path}[/green]")

@app.command(help="Show an overview of the animals at a reserve")
def reserve(
   reserve_name: config.Reserve = typer.Argument(config.Reserve.hirsch), 
   species: Optional[bool] = typer.Option(True, help="Include the species names"),
   modded: Optional[bool] = typer.Option(False, "--modded", "-m", help="Use modded version of the reserve")
) -> None:
  reserve_details = commands.describe_reserve(reserve_name, modded, species, state["verbose"])
  console.print(reserve_details)

@app.command(help="Shows all the reserve names")
def reserves() -> None:
  reserve_names = commands.reserves()
  console.print(reserve_names)
  

@app.command(help="Show the animal species at a reserve")
def animals(
   reserve_name: config.Reserve = typer.Argument(config.Reserve.hirsch), 
   species: str = typer.Argument(..., help="Animal species to see"),
   good: Optional[bool] = typer.Option(False, "--good", "-g", help="Only show diamonds and GOs"),
   modded: Optional[bool] = typer.Option(False, "--modded", "-m", help="Use modded version of the reserve")
) -> None:
  animal_details = commands.describe_animals(reserve_name, species, good, modded, state["verbose"])
  console.print(animal_details)

@app.command(help="Shows all the species found at a reserve")
def species(reserve_name: config.Reserve = typer.Argument(config.Reserve.hirsch)) -> None:
  species = commands.species(reserve_name)
  console.print(species)

@app.command(help="Modify the animals for a specific reserve and species")
def mod(
   reserve_name: config.Reserve = typer.Argument(config.Reserve.hirsch), 
   species: config.ModifiableSpecies = typer.Argument(...),
   strategy: config.Strategy = typer.Argument(...),
   modifier: int = typer.Argument(None, help="used to modify strategy; usually a percentage", min=1, max=100),
   rares: Optional[bool] = typer.Option(False, "--rares", "-r", help="Include rare and super rare furs"),
   modded: Optional[bool] = typer.Option(False, "--modded", "-m", help="Use modded version of the reserve")
) -> None:
   mod_result = commands.mod(reserve_name, species, strategy, modifier, rares, modded, state["verbose"])
   print(f"[yellow]You can find the modded file at: {config.MOD_DIR_PATH}[/yellow]")
   print()
   console.print(mod_result)

@app.command(help="Debug command to parse and save compressed ADF as text file")
def parse(filename: str = typer.Argument(...)):
   commands.parse(filename, state["verbose"])
   console.print(f"[green]File {filename} parsed[/green]")

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v")
) -> None:
    """
    Animal Population Changer
    """
    if verbose:
       print("[yellow]Using verbose mode[/yellow]")
       state["verbose"] = True