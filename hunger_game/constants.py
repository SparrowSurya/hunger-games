"""
This modules containts the necessary constants.
"""

import pathlib


__all__ = (
    "BRAWLER_DATA_FP",
    "MODES_DATA_FP",
    "NARRATION_DATA_FP",
)


DATA_DIR = "data"

BRAWLERS_FILE = "brawlers.json"
MODES_FILE = "modes.json"
NARRATIONS_FILE = "narrations.json"

BRAWLER_DATA_FP = str(pathlib.Path(DATA_DIR, BRAWLERS_FILE))
MODES_DATA_FP = str(pathlib.Path(DATA_DIR, MODES_FILE))
NARRATION_DATA_FP = str(pathlib.Path(DATA_DIR, NARRATIONS_FILE))
