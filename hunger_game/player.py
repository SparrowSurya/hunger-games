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
    """Describes the behavioral traits of a player."""

    AGGRESSIVE = auto()
    """High risk-taker. Prioritizes attacking even when at a health disadvantage."""

    CAUTIOUS = auto()
    """Survival-focused. Prioritizes healing when damaged."""

    COLLECTOR = auto()
    """Loot-focused. Prioritizes finding and collecting cubes."""

    CAMPER = auto()
    """Passive survivalist. Prefers to stay hidden to avoid conflict."""

    AMBUSER = auto()
    """Tactical hunter. Prefers hiding specifically to launch surprise attacks."""

    TEAMER = auto()
    """Social brawler. Prefers teaming with others and always accepts offers."""

    BACKSTABBER = auto()
    """Deceptive ally. Always accepts teamups to lure victims for a betrayal."""


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
