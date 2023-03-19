# animal-population-changer

A tool that allows anyone to change the animal population on all the reserves in theHunter: Call of the Wild (COTW). I have started out with the CLI, but I plan on building a simple GUI also.

Currently the tool only supports modifying the following species:
1. Red Deer
1. Whitetail Deer
1. Black Bear
1. Moose

The following mods are possible with this tool:
1. Make all males Great Ones.
1. Make a Great One male for every fur type (e.g., since moose have 6 furs, this would make 6 males a Great One).
1. Make some males a Great One, where you tell the tool what percentage you want to be a Great One.
1. Make all males a Diamond. This will not affect Great Ones.
1. Make some males a Diamond, where you tell the tool what percentage you want to be a Diamond.

This tool was tested on Windows 11 with the game installed via Steam. If your game files are saved somewhere else besides where Steam saves them, use the `apc set-save [SAVE_PATH]` command to tell the tool which path to use.

The modded population files can be found at the following directory: `C:\Users\{username}\Documents\APC\mods`.

## How To Build

| Note: This code was built and tested with Python 3.10.10.

You can install a developer version by using:
```sh
pip install .
```

If you want to build a wheel:
```sh
pip install -U build
python -m build
pip install dist/apc-0.1.0-py3-none-any.whl
```

If you want to build an executable (i.e., from Windows):
```sh
pip install -U pyinstaller
pyinstaller apc.py
./dist/apc.exe
```

## Command-Line Interface

There are several available commands. You can see them all by typing:

```sh
apc --help
```
This will output something similar to this:
```text
Usage: apc [OPTIONS] COMMAND [ARGS]...

  Animal Population Changer

Options:
  --version                       Show the application's version and exit.
  -v, --verbose
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  mod        Modify the animals for a specific reserve and species
  parse      Debug command to parse and save compressed ADF as text file
  reserve    Show an overview of the animals at a reserve
  reserves   Shows all the reserve names
  set-save   Set the location of animal population files
  show-save  Show the location of animal population files
  species    Shows all the species found at a reserve
```

The most important command is `mod` which will modify an animal population file. The signature of this command is the following:
```text
mod [-m] [RESERVE_NAME] SPECIES STRATEGY [MODIFIER] 
```

The `-m` option is to tell the command if you want to modify the game population file or the existing modded population file. This allows you to make multiple modifications to the population file. The `RESERVE_NAME` argument is which reserve you want to modify. If you want to know the reserve names use the `apc reserves` command and it will show you the reserve names along with their key values. The `SPECIES` argument is the specific species you want to modify. You can see all species for a reserve by using the command `apc species [RESERVE_NAME]`. The `STRATEGY` argument has five possible values: `go-all`, `go-furs`, `go-some`, `diamond-all`, and `diamond-some`. The `MODIFIER` optional argument only applies to the `go-some` and `diamond-some` strategies, where the value is a percentage of the animals you want modified (percentage can be from 1 to 100).

## Example Usage

To see the reserve names:
```sh
apc reserves
```

To show the existing animals in the Layton Lakes reserve:
```sh
apc reserve layton
```

Then to add one of each moose Great One furs to the population:
```sh
apc mod layton moose go-furs
```

I also want to add some diamonds (30%), so I'm going to use the `-m` option to modify again:
```sh
apc mod -m layton moose diamon-some 30
```

That's it. I have modified the moose on the Layton Lakes reserve. For my computer, I copied the modded file located at `C:\Users\appma\Documents\APC\mods\animal_population_1` to my saved games folder.
