"""
This module provide player class:
* `Player`
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
    """Behavioral traits that influence brawler decision-making and performance."""

    AGGRESSIVE = auto()
    """Higher attack frequency and damage output."""

    CAUTIOUS = auto()
    """Prioritizes healing and defensive positioning."""

    COLLECTOR = auto()
    """Prioritizes looting and resource gathering."""

    CAMPER = auto()
    """Prefers hiding and setting up ambushes."""

    AMBUSER = auto()
    """Specializes in high-damage surprise strikes."""

    TEAMER = auto()
    """More likely to attempt alliances."""

    BACKSTABBER = auto()
    """Higher tendency to betray allies for massive damage."""

@dataclass(repr=False)
class Player:
    """Player information and its brawler's state.."""

    id: str
    """A unique identifier for the player instance."""

    name: str
    """The display name of the human or AI player."""

    info: BrawlerInfo
    """The static brawler type and stats (from JSON)."""

    state: BrawlerState
    """The current dynamic state of the brawler (HP, last action, etc.)."""

    traits: List[Tuple[PlayerTrait, float]]
    """Behavioral traits and their intensities that drive decision weights."""

    def __post_init__(self):
        self.state.hp = self.info.hitpoints
