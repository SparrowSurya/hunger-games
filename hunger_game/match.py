"""
This module provide the match classes:
* `MatchEvent`
* `MatchState`
* `MatchConfig`
* `EncounterState`
* `Encounter`
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
    "EncounterState",
    "Encounter",
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


class EncounterState(StrEnum):
    """Defines the state of a localized interaction between players."""

    ISOLATED = auto()  # Wandering alone
    DUEL = auto()  # 1v1 fight
    MELEE = auto()  # 3+ player chaotic fight


@dataclass
class Encounter:
    """Represents a localized skirmish or situation in the match."""

    participants: List[Player]
    state: EncounterState
    age: int = 0


@dataclass(repr=False)
class MatchState:
    """Describes one narrative match among brawlers."""

    environment: GameModeEnv
    players: List[Player]
    eliminations: List[Tuple[Player | GameModeDynamic, Player]] = field(  # pyright: ignore[reportUnknownVariableType]
        default_factory=list
    )
    encounters: List[Encounter] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]


@dataclass(repr=False)
class MatchConfig:
    """Describes the general match engine parameters."""

    damage_variance: int = 5
    heal_min: int = 10
    heal_max: int = 25

    # Match Phase thresholds (% of players remaining)
    mid_game_threshold: float = 0.7
    end_game_threshold: float = 0.3

    # Narration specifics
    intro_frequency: float = 0.15

    # Interaction settings
    encounter_merge_chance: float = 0.3
    third_party_chance: float = 0.1
