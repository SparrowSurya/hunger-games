"""
This modules provides game mode related classes:
* `GameMode`
* `GameModeObjective`
* `GameModeConfig`
* `GameModeDynamic`
* `GameModeEnv`
* `Collectable`
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import List


__all__ = (
    "GameMode",
    "GameModeObjective",
    "GameModeConfig",
    "GameModeDynamic",
    "GameModeEnv",
    "Collectable",
)


class GameMode(StrEnum):
    """Game mode in the game."""

    SOLO_SHOWDOWN = auto()


class GameModeObjective(StrEnum):
    """Objective of the game mode."""

    LAST_PLAYER_STANDING = auto()


@dataclass(repr=False)
class GameModeConfig:
    """Game mode configuration."""

    players: int
    objective: GameModeObjective


class GameModeDynamic(StrEnum):
    """Game mode dynamic components."""

    POISON_GAS = auto()


@dataclass(repr=False)
class GameModeEnv:
    """Game mode environment."""

    mode: GameMode
    config: GameModeConfig
    dynamics: List[GameModeDynamic] = field(default=list)  # type: ignore


class Collectable(StrEnum):
    """Represents a collectable item in game mode."""

    CUBE = auto()
    GEM = auto()
