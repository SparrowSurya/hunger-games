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
    "BrawlerNature",
    "BrawlerInfo",
    "BrawlerState",
)


class BrawlerAction(StrEnum):
    """Describes brawler actions in game."""

    ATTACK = auto()
    """Engaging an enemy to deal damage."""

    HEAL = auto()
    """Recovering health points over time."""

    LOOT = auto()
    """Searching for power cubes or equipment."""

    CAMP = auto()
    """Hiding in bushes to avoid detection or set up ambushes."""

    AMBUSH = auto()
    """Striking an unsuspecting enemy from concealment."""

    TEAMUP = auto()
    """Attempting to form a temporary alliance with another player."""

    BETRAY = auto()
    """Attacking an ally to break an alliance and deal massive damage."""


class BrawlerNature(StrEnum):
    """Describes the class/nature of a brawler, influencing logic and narrations."""

    DAMAGE_DEALER = auto()
    """High consistent damage output."""

    SNIPER = auto()
    """Long-range precision specialists."""

    TANK = auto()
    """High durability, designed to soak up damage."""

    ASSASSIN = auto()
    """High mobility and burst damage for quick eliminations."""

    CONTROLLER = auto()
    """Zoning specialists that restrict enemy movement."""

    ARTILLERY = auto()
    """Throwers that deal damage over obstacles."""

    SUPPORT = auto()
    """Provides utility, such as healing or buffs, to themselves or allies."""

    ANTI_TANK = auto()
    """Specialists designed to take down high-HP targets."""

@dataclass(repr=False)
class BrawlerInfo:
    """Static information about a brawler loaded from data."""

    name: str
    """The type name of the brawler (e.g., Shelly, Colt)."""

    nature: BrawlerNature
    """The brawler's class/nature used for verb selection and logic."""

    damage: int
    """Base attack damage value."""

    hitpoints: int
    """Maximum health points."""


@dataclass(repr=False)
class BrawlerState:
    """Dynamic state of the brawler during a match."""

    hp: int = 0
    """Current health points."""

    current_max_hp: int = 0
    """Current maximum health points, including power cube bonuses."""

    power_cubes: int = 0
    """Number of power cubes collected, boosting health and damage."""

    action_weights: Dict[BrawlerAction, float] = field(default_factory=dict)
    """Dynamic weights for each possible action type."""

    last_action: BrawlerAction | None = None
    """The most recent action performed, used for mood and logic context."""

    @property
    def alive(self) -> bool:
        """Returns True if the brawler's health is above zero."""
        return self.hp > 0
