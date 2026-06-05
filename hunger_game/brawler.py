"""
This module provides brawler related classes:
* `BrawlerNature`
* `BrawlerAction`
* `BrawlerAttack`
* `BrawlerEngagement`
* `Brawler`
* `BrawlerInfo`
* `BrawlerState`
"""


from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Dict, override


__all__ = (
    "BrawlerNature",
    "BrawlerAction",
    "BrawlerAttack",
    "BrawlerEngagement",
    "Brawler",
    "BrawlerInfo",
    "BrawlerState",
)


class BrawlerNature(StrEnum):
    """Describes the nature of brawlers in the game."""

    DAMAGE_DEALER = auto()
    SNIPER = auto()
    TANK = auto()
    ASSASSIN = auto()
    CONTROLLER = auto()
    ARTILLERY = auto()
    SUPPORT = auto()
    ANTI_TANK = auto()


class BrawlerAction(StrEnum):
    """Describes brawler actions in game."""

    ATTACK = auto()
    HEAL = auto()


class BrawlerAttack(StrEnum):
    """Describes the attack delivery mechanism in game."""

    PROJECTILE = auto()
    SPREAD = auto()
    MELEE = auto()
    THROWABLE = auto()
    PIERCING = auto()


class BrawlerEngagement(StrEnum):
    """Describes the engagement/mood of the brawler."""

    EXPOSED = auto()
    HEALING = auto()


class Brawler(StrEnum):
    """Playable bralwers in the game."""

    SHELLY = auto()
    NITA = auto()
    COLT = auto()
    BULL = auto()
    JESSIE = auto()
    BROCK = auto()
    DYNAMIKE = auto()
    TICK = auto()
    EMZ = auto()
    BO = auto()
    EIGHT_BIT = auto()

    @override
    def __str__(self) -> str:
        return self.name.lower().replace('eight_', '8-').capitalize()


@dataclass(repr=False)
class BrawlerInfo:
    """Static information about a brawler."""

    brawler: Brawler
    nature: BrawlerNature
    attack: BrawlerAttack
    actions: Dict[BrawlerAction, float]
    damage: int
    hitpoints: int



@dataclass(repr=False)
class BrawlerState:
    """State of the brawler in the match."""

    hp: int = 0
    engagement: BrawlerEngagement = BrawlerEngagement.EXPOSED

    @property
    def alive(self) -> bool: return self.hp > 0
