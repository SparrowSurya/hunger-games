"""
This module provides brawler related classes:
* `BrawlerAction`
* `BrawlerInfo`
* `BrawlerState`
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Dict


__all__ = (
    "BrawlerAction",
    "BrawlerInfo",
    "BrawlerState",
)


class BrawlerAction(StrEnum):
    """Describes brawler actions in game."""

    ATTACK = auto()
    HEAL = auto()
    LOOT = auto()
    CAMP = auto()
    AMBUSH = auto()


@dataclass(repr=False)
class BrawlerInfo:
    """Static information about a brawler loaded from data."""

    name: str
    nature: str
    actions: Dict[BrawlerAction, float]
    damage: int
    hitpoints: int


@dataclass(repr=False)
class BrawlerState:
    """Dynamic state of the brawler during a match."""

    hp: int = 0
    last_action: BrawlerAction | None = None

    @property
    def alive(self) -> bool:
        return self.hp > 0
