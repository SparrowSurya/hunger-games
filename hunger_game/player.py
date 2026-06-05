"""
This module provide player class:
* `Player`
* `PlayerTrait`
"""

from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Tuple, List

from hunger_game.brawler import BrawlerInfo, BrawlerState


__all__ = (
    "Player",
    "PlayerTrait",
)


class PlayerTrait(StrEnum):
    """Describes the behavioral traits of a player.

    These traits influence both the decision-making in the simulator (action weights)
    and the stylistic choices in the narration engine.
    """

    AGGRESSIVE = auto()
    """High risk-taker. Prioritizes attacking even when at a health disadvantage."""

    CAUTIOUS = auto()
    """Survival-focused. Prioritizes healing and staying hidden when damaged."""

    COLLECTOR = auto()
    """Power-hungry. Prioritizes collecting power cubes over combat or survival."""

    CAMPER = auto()
    """Passive survivalist. Prefers to find a bush and stay hidden to avoid conflict."""

    AMBUSER = auto()
    """Tactical hunter. Prefers hiding in bushes specifically to launch surprise attacks."""

    TEAMER = auto()
    """Socially active. High likelihood of spinning to form alliances with others."""

    TRAITOR = auto()
    """Deceptive player. High likelihood of joining alliances only to betray them for easy kills."""

    LAZY = auto()
    """Low activity. Often chooses to do nothing or stay put instead of moving or attacking."""


@dataclass(repr=False)
class Player:
    """Player information and its brawler's state.."""

    id: str
    name: str
    info: BrawlerInfo
    state: BrawlerState
    traits: List[Tuple[PlayerTrait, float]]

    def __post_init__(self):
        self.state.hp = self.info.hitpoints
