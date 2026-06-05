"""
Hunger Game Simulation Package.

This package provides a zero-player simulation engine inspired by battle royale
mechanics. It includes modules for managing brawlers, game modes, match state,
and a simulator that narrates events through an observer-based narration system.

Main Components:
- `simulator`: Core engine for running match moments.
- `narrator`: Event-based narration logic.
- `player`: Player state and brawler information management.
- `game_mode`: Definitions for different rulesets and environments.
"""

# ruff: noqa: F403, F405

from hunger_game.brawler import *
from hunger_game.constants import *
from hunger_game.game_mode import *
from hunger_game.match import *
from hunger_game.player import *
from hunger_game.narrator import *
from hunger_game.text_narrator import *
from hunger_game.simulator import *
from hunger_game.utils import *
