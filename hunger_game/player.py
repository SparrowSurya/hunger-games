"""
This module provide player class:
* `Player`
"""

from dataclasses import dataclass

from hunger_game.brawler import BrawlerInfo, BrawlerState


__all__ = (
    "Player",
)


@dataclass(repr=False)
class Player:
    """Player information and its brawler's state.."""

    id: str
    name: str
    info: BrawlerInfo
    state: BrawlerState

    def __post_init__(self):
        self.state.hp = self.info.hitpoionts
