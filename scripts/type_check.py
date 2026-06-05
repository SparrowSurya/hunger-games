import subprocess
import sys


def run_type_check():
    """Runs pyright on the project."""
    print("Running type check (pyright)...")
    try:
        # We check the core package and the main entry point
        subprocess.run(["pyright", "hunger_game/", "main.py"], check=True)
        print("Success: No type errors found!")
    except subprocess.CalledProcessError as e:
        # pyright returns non-zero if errors are found
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Error: 'pyright' command not found. Please run 'uv sync' or install pyright.")
        sys.exit(1)


if __name__ == "__main__":
    run_type_check()
