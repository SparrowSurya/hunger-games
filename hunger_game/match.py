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
from typing import List, Tuple, Set

from hunger_game.game_mode import GameModeEnv, GameModeDynamic
from hunger_game.player import Player


__all__ = (
    "MatchState",
    "MatchConfig",
    "EncounterState",
    "Encounter",
)


class EncounterState(StrEnum):
    """Defines the state of a localized interaction between players."""

    ISOLATED = auto()
    """Wandering alone."""

    DUEL = auto()
    """1v1 fight."""

    MELEE = auto()
    """3+ player chaotic fight."""

@dataclass
class Encounter:
    """Represents a localized skirmish or situation in the match."""

    participants: List[Player]
    """The list of players currently involved in this specific encounter."""

    state: EncounterState
    """The current nature of the encounter (e.g., ISOLATED, DUEL, MELEE)."""

    age: int = 0
    """How many moments this encounter has persisted."""

    alliances: List[Set[str]] = field(default_factory=list)
    """Groups of allied player IDs within this encounter."""


@dataclass(repr=False)
class MatchState:
    """Describes one narrative match among brawlers."""

    environment: GameModeEnv
    """The game mode and environmental dynamics for this match."""

    players: List[Player]
    """All players participating in the match."""

    eliminations: List[Tuple[Player | GameModeDynamic, Player]] = field(
        default_factory=list
    )
    """Record of who eliminated whom, used for final rankings."""

    encounters: List[Encounter] = field(default_factory=list)
    """The list of active localized skirmishes on the map."""


@dataclass(repr=False)
class MatchConfig:
    """Describes the general match engine parameters."""

    intro_frequency: float = 0.35
    """Probability (0-1) that a brawler action will include a mood-based intro."""

    encounter_merge_chance: float = 0.3
    """Probability that two isolated players will find each other and start a duel."""

    third_party_chance: float = 0.1
    """Probability that an isolated player will join an existing skirmish."""
