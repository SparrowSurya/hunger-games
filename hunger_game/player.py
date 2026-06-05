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
