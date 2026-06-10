"""
This module provides the match event models:
* `MatchEventModel`
* `MatchBeginEvent`
* `MatchEndEvent`
* `MomentBeginEvent`
* `MomentEndEvent`
* `AttackEvent`
* `HealEvent`
* `LootEvent`
* `CampEvent`
* `AmbushEvent`
* `PoisonDamageEvent`
* `TeamupEvent`
* `BetrayalEvent`
* `PoisonGasStartEvent`
* `PoisonGasCoverageEvent`
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hunger_game.match import MatchState
    from hunger_game.player import Player


__all__ = (
    "MatchEventModel",
    "MatchBeginEvent",
    "MatchEndEvent",
    "MomentBeginEvent",
    "MomentEndEvent",
    "AttackEvent",
    "HealEvent",
    "LootEvent",
    "CampEvent",
    "AmbushEvent",
    "PoisonDamageEvent",
    "TeamupEvent",
    "BetrayalEvent",
    "PoisonGasStartEvent",
    "PoisonGasCoverageEvent",
)


@dataclass
class MatchEventModel:
    """Base class for all match events."""


@dataclass
class MatchBeginEvent(MatchEventModel):
    state: MatchState
    """The initial state of the match at commencement."""


@dataclass
class MatchEndEvent(MatchEventModel):
    state: MatchState
    """The final state of the match when completed."""

    winner: Player | None
    """The brawler who won the match, or None if no winner."""


@dataclass
class MomentBeginEvent(MatchEventModel):
    moment: int
    """The sequential number of the moment starting."""


@dataclass
class MomentEndEvent(MatchEventModel):
    alive_count: int
    """Number of brawlers remaining in the match."""

    eliminated: list[Player]
    """List of brawlers who were eliminated during this specific moment."""


@dataclass
class AttackEvent(MatchEventModel):
    attacker: Player
    """The brawler performing the attack."""

    target: Player
    """The brawler receiving the damage."""

    damage: int
    """The amount of damage dealt (raw value)."""


@dataclass
class HealEvent(MatchEventModel):
    healed: Player
    """The brawler receiving the healing."""

    healer: Player | None
    """The brawler providing the healing, or None if self-regeneration."""


@dataclass
class LootEvent(MatchEventModel):
    player: Player
    """The brawler collecting power cubes or supplies."""


@dataclass
class CampEvent(MatchEventModel):
    player: Player
    """The brawler hiding in foliage to avoid conflict."""


@dataclass
class AmbushEvent(MatchEventModel):
    attacker: Player
    """The brawler attacking from concealment."""

    target: Player
    """The unsuspecting victim of the surprise attack."""

    damage: int
    """The amount of damage dealt (raw value)."""


@dataclass
class PoisonDamageEvent(MatchEventModel):
    player: Player
    """The brawler taking damage from the environmental gas."""

    damage: int
    """The amount of poison damage taken."""

    context: str
    """The reason for the damage (e.g., 'lazy', 'cornered', 'coverage')."""

    silent: bool = False
    """If True, no narration should be emitted for this specific damage instance."""


@dataclass
class TeamupEvent(MatchEventModel):
    initiator: Player
    """The brawler offering the teamup."""

    target: Player
    """The brawler receiving the offer."""

    outcome: str
    """The result of the offer ('ACCEPT', 'REJECT', 'ATTACK')."""

    damage: int = 0
    """Damage dealt if the outcome was 'ATTACK'."""


@dataclass
class BetrayalEvent(MatchEventModel):
    betrayer: Player
    """The brawler performing the backstab."""

    victim: Player
    """The unsuspecting ally."""

    damage: int
    """The amount of damage dealt (raw value)."""


@dataclass
class PoisonGasStartEvent(MatchEventModel):
    """Event triggered when the poison gas begins to enter the arena."""

    pass


@dataclass
class PoisonGasCoverageEvent(MatchEventModel):
    """Event triggered when the poison gas has fully engulfed the entire arena."""

    pass
