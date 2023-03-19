from apc import cli, __app_name__, adf
from pathlib import Path

def main():
    cli.app(prog_name=__app_name__)

if __name__ == "__main__":
    main()