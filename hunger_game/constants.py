"""
This modules containts the necessary constants.
"""

import pathlib
from hunger_game.utils import json_file


__all__ = (
    "BRAWLER_DATA_FP",
    "MODES_DATA_FP",
    "NARRATION_DATA_FP",
)


DATA_DIR = pathlib.Path(__file__).parent.parent / "data"

BRAWLERS_FILE = json_file("brawlers", str(DATA_DIR))
MODES_FILE = json_file("modes", str(DATA_DIR))
NARRATIONS_FILE = json_file("narrations", str(DATA_DIR))

BRAWLER_DATA_FP = str(BRAWLERS_FILE)
MODES_DATA_FP = str(MODES_FILE)
NARRATION_DATA_FP = str(NARRATIONS_FILE)
