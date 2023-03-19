from typing import Optional
from rich import print
from rich.console import Console
from apc import commands

import typer

from apc import __app_name__, __version__, config

app = typer.Typer()
console = Console()
state = { "verbose": False }

@app.command(name="set-save", help="Set the location where the game's animal population files are located")
def set_save(save_path: str = typer.Argument(...)) -> None:
  config.save_path(save_path)
  print(f"[green]The save path {save_path} has been saved[/green]")

@app.command(name="show-save", help="Show the location where the game's animal population files are located")
def show_save() -> None:
  save_path = config.get_save_path()
  print(f"[green]The save path is {save_path}[/green]")

@app.command(help="Show an overview of the animals at a reserve")
def reserve(
   reserve_name: str = typer.Argument("layton"), 
   species: Optional[bool] = typer.Option(True, help="Include the species names"),
   modded: Optional[bool] = typer.Option(False, "--modded", "-m", help="Use modded version of the reserve")
) -> None:
  reserve_details = commands.describe_reserve(reserve_name, modded, species, state["verbose"])
  console.print(reserve_details)

@app.command(help="Shows all the reserve names")
def reserves() -> None:
  reserve_names = commands.reserves()
  console.print(reserve_names)
  
@app.command(help="Shows all the species found at a reserve")
def species(reserve_name: str = typer.Argument("layton")) -> None:
  species = commands.species(reserve_name)
  console.print(species)

@app.command(help="Modify the animals for a specific reserve and species")
def mod(
   reserve_name: str = typer.Argument("layton"), 
   species: str = typer.Argument(...),
   strategy: str = typer.Argument(...),
   modifier: int = typer.Argument(None, help="modifies the strategy"),
   modded: Optional[bool] = typer.Option(False, "--modded", "-m", help="Use modded version of the reserve")
) -> None:
   mod_result = commands.mod(reserve_name, species, strategy, modifier, modded, state["verbose"])
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
        "-v",
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
       print("[red]Using verbose mode[/red]")
       state["verbose"] = True