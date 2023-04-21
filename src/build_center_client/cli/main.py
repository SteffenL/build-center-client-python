from .commands.parser import parse_args
from .commands.run import run_app

def main_cli():
    run_app(parse_args())

if __name__ == "__main__":
    main_cli()
