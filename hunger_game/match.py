"""
This module provide the match classes:
* `MatchEvent`
* `MatchState`
* `MatchConfig`
"""


from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import List, Tuple

from hunger_game.game_mode import GameModeEnv, GameModeDynamic
from hunger_game.player import Player


__all__ = (
    "MatchEvent",
    "MatchState",
    "MatchConfig",
)


class MatchEvent(StrEnum):
    """Describes an event in the match."""

    MATCH_BEGIN = auto()
    MATCH_END = auto()
    MOMENT_BEGIN = auto()
    MOMENT_END = auto()
    ATTACK = auto()
    HEALING = auto()
    POSION_GAS = auto()


@dataclass(repr=False)
class MatchState:
    """Describes one narrative match among brawlers."""

    environment: GameModeEnv
    players: List[Player]
    eliminations: List[Tuple[Player | GameModeDynamic, Player]] = field(default_factory=list)


@dataclass(repr=False)
class MatchConfig:
    """Describes the decision bias and pacing of the match."""

    # Combat
    damage_variance: int = 5
    heal_min: int = 10
    heal_max: int = 25

    # Poison Gas Config
    gas_initial_frequency: int = 2
    gas_escalation_after_iterations: int = 5
    gas_hit_chance: float = 0.2
    gas_escalated_hit_chance: float = 1.0
    gas_damage: int = 15

    # Match Phase thresholds (% of players remaining)
    mid_game_threshold: float = 0.7
    end_game_threshold: float = 0.3
