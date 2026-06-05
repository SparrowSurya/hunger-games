import subprocess
import sys


def run_format():
    """Runs ruff format on the package."""
    print("Formatting code with Ruff...")
    try:
        subprocess.run(
            ["ruff", "format", "hunger_game/", "main.py", "scripts/"], check=True
        )
        print("Success: Code formatted!")
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Error: 'ruff' command not found. Please install it.")
        sys.exit(1)


if __name__ == "__main__":
    run_format()
