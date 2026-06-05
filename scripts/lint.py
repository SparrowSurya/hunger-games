import subprocess
import sys


def run_lint():
    """Runs ruff check on the package."""
    try:
        subprocess.run(["ruff", "check", "hunger_game/"], check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Error: 'ruff' command not found. Please install it.")
        sys.exit(1)


if __name__ == "__main__":
    run_lint()
