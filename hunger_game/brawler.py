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
    """Describes the nature of brawlers in the game.

    This classification helps to identify the nature of the brawler allowing benefit from
    some situations whereever applicable.
    """

    DAMAGE_DEALER = auto()
    """
    Benefits from sustained, mid-range combat and consistent damage output to win
    prolonged trades.
    """

    SNIPER = auto()
    """
    Benefits from long-range encounters in open spaces, excels at picking off EXPOSED
    or ESCAPING targets.
    """

    TANK = auto()
    """
    Benefits from high durability and close-quarters combat, excels at surviving
    AMBUSHED situations or gas.
    """

    ASSASSIN = auto()
    """
    Benefits from stealth and mobility, excels at quickly eliminating low-HP or squishy
    targets when CAMPING.
    """

    CONTROLLER = auto()
    """
    Benefits from area denial, excellent at restricting movement and forcing enemies
    into POISON_GAS.
    """

    ARTILLERY = auto()
    """
    Benefits from attacking over obstacles, capable of flushing out enemies who are
    CAMPING behind cover.
    """

    SUPPORT = auto()
    """
    Benefits from cooperative play and TEAM_UP actions, providing utility and reducing
    BETRAY risks.
    """

    ANTI_TANK = auto()
    """
    Benefits from targeting high-HP brawlers, countering the survivability of TANKS in
    combat.
    """


class BrawlerAction(StrEnum):
    """Describes brawler actions in game.

    It is used to decide the actions done by brawer during the moment.
    """

    NOTHING = auto()
    """Brawler decided to do nothing."""

    ATTACK = auto()
    """Brawler decided to attack other brawler."""

    BUSH_CAMP = auto()
    """Brawler decided to camp in bush."""

    HEAL = auto()
    """Brawler decided to heal."""

    TEAM_UP = auto()
    """Brawler decieds to teamup with enemy."""

    COLLECT = auto()
    """Brawler decieds to collect gems/powercubes."""

    STAY_HIDDEN = auto()
    """brawler decides to stay hidden in bushes."""

    BETRAY = auto()
    """Brawler decides to betray their teamed up enemy."""


class BrawlerAttack(StrEnum):
    """Describes the attack delivery mechanism in game."""

    PROJECTILE = auto()
    """Straight line based projectile."""

    SPREAD = auto()
    """Concic shape based attack."""

    MELEE = auto()
    """Short range attack."""

    THROWABLE = auto()
    """Attacks that can be thrown over the walls."""

    PIERCING = auto()
    """Attack that bounces or pierces throught brawler or environment."""


class BrawlerEngagement(StrEnum):
    """Describes the engagement of the brawler.

    This decides the engagement state of brawler from one moment to next moment.
    """

    COLLECTING = auto()
    CAMPING = auto()
    AMBUSHED = auto()
    TEAMING = auto()
    EXPOSED = auto()
    ESCAPING = auto()
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
    cubes: int = 0
    gems: int = 0
    hidden: bool = False
    engagement: BrawlerEngagement = BrawlerEngagement.EXPOSED

    @property
    def alive(self) -> bool: return self.hp > 0
