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
class PoisonGasConfig:
    """Configuration for poison gas dynamics."""

    safe_until: int
    """The moment until which the map is completely safe from poison gas."""

    full_coverage_at: int
    """The moment at which the poison gas covers the entire map."""

    base_damage: int
    """The starting damage value for poison gas."""

    scaling_factor: float
    """The percentage increase in gas damage per moment after full coverage."""

    random_hit_chance: float
    """Baseline chance for any player to be grazed by gas during creeping phase."""

    lazy_hit_chance: float
    """Higher chance for CAMPING or ISOLATED players to take gas damage."""

    cornered_hp_threshold: float
    """HP ratio below which a player is considered 'cornered' during combat."""

    cornered_hit_chance: float
    """Chance for a 'cornered' player to take gas damage when attacked."""


@dataclass(repr=False)
class GameModeConfig:
    """Configuration for a game mode, loaded from data."""

    max_players: int
    """Maximum players allowed in this mode."""

    damage_variance: int
    """Random spread added or subtracted from a brawler's base damage."""

    heal_min: int
    """Minimum HP restored during a HEAL action."""

    heal_max: int
    """Maximum HP restored during a HEAL action."""

    mid_game_threshold: float
    """Percentage of players remaining to trigger mid-game aggression levels."""

    end_game_threshold: float
    """Percentage of players remaining to trigger end-game aggression levels."""

    gas: PoisonGasConfig | None = None
    """Poison gas configuration if the mode includes it."""


@dataclass(repr=False)
class GameModeEnv:
    """Environment for a game mode."""

    name: str
    objective: GameModeObjective
    dynamics: list[GameModeDynamic]
    config: GameModeConfig
