"""
This module provides brawler related classes:
* `BrawlerAction`
* `BrawlerInfo`
* `BrawlerState`
"""

from __future__ import annotations
from dataclasses import dataclass, field
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
    """The type name of the brawler (e.g., Shelly, Colt)."""

    nature: str
    """The brawler's class/nature (e.g., SNIPER, TANK) used for verb selection."""

    damage: int
    """Base attack damage value."""

    hitpoints: int
    """Maximum health points."""


@dataclass(repr=False)
class BrawlerState:
    """Dynamic state of the brawler during a match."""

    hp: int = 0
    """Current health points."""

    action_weights: Dict[BrawlerAction, float] = field(default_factory=dict)
    """Dynamic weights for each possible action type."""

    last_action: BrawlerAction | None = None
    """The most recent action performed, used for mood and logic context."""

    @property
    def alive(self) -> bool:
        """Returns True if the brawler's health is above zero."""
        return self.hp > 0
