"""
This modules provides game mode related classes:
* `GameModeObjective`
* `GameModeConfig`
* `GameModeDynamic`
* `GameModeEnv`
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum, auto


__all__ = (
    "GameModeObjective",
    "GameModeConfig",
    "GameModeDynamic",
    "GameModeEnv",
)


class GameModeObjective(StrEnum):
    """Represents the objective of a game mode."""

    LAST_PLAYER_STANDING = auto()


class GameModeDynamic(StrEnum):
    """Represents a dynamic event in a game mode."""

    POISON_GAS = auto()


@dataclass(repr=False)
class GameModeConfig:
    """Configuration for a game mode, loaded from data."""

    max_players: int
    damage_variance: int
    heal_min: int
    heal_max: int
    mid_game_threshold: float
    end_game_threshold: float
    gas_initial_frequency: int
    gas_escalation_after_iterations: int
    gas_hit_chance: float
    gas_escalated_hit_chance: float
    gas_damage: int


@dataclass(repr=False)
class GameModeEnv:
    """Environment for a game mode."""

    name: str
    objective: GameModeObjective
    dynamics: list[GameModeDynamic]
    config: GameModeConfig
