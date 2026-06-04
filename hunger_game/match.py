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
    BUSH_CAMP = auto()
    HEALING = auto()
    TEAMUP = auto()
    COLLECT = auto()
    HIDING = auto()
    BETRAY = auto()
    POSION_GAS = auto()


@dataclass(repr=False)
class MatchState:
    """Describes one narrative match among brawlers."""

    environment: GameModeEnv
    players: List[Player]
    eliminations: List[Tuple[Player | GameModeDynamic, Player]] = field(default_factory=list) # type: ignore


@dataclass(repr=False)
class MatchConfig:
    """Describes the decision bais of the match."""

    # p_teamup: float
    # p_betray: float
