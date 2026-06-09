"""
This module provide match observer class:
* `MatchObserver`
"""

from __future__ import annotations
import abc
from typing import TYPE_CHECKING

from hunger_game.events import (
    MatchBeginEvent,
    MatchEndEvent,
    MomentBeginEvent,
    MomentEndEvent,
    AttackEvent,
    HealEvent,
    LootEvent,
    CampEvent,
    AmbushEvent,
    PoisonDamageEvent,
    PoisonGasStartEvent,
    PoisonGasCoverageEvent,
)

if TYPE_CHECKING:
    from hunger_game.simulator import MatchSimulator


__all__ = ("MatchObserver",)


class MatchObserver(abc.ABC):
    """Observes the events in the match.

    This helps to observe the events happening in match which can be further passed to
    narrator for event narration.
    """

    sim: MatchSimulator

    def __init__(self, simulator: MatchSimulator):
        self.sim = simulator

    @abc.abstractmethod
    def on_match_begin(self, event: MatchBeginEvent):
        """Match start event."""

    @abc.abstractmethod
    def on_match_end(self, event: MatchEndEvent):
        """Match end event."""

    @abc.abstractmethod
    def on_match_moment_begin(self, event: MomentBeginEvent):
        """Match moment beginning."""

    @abc.abstractmethod
    def on_match_moment_end(self, event: MomentEndEvent):
        """Match moment ending."""

    @abc.abstractmethod
    def on_attack(self, event: AttackEvent):
        """Player attacks someone."""

    @abc.abstractmethod
    def on_heal(self, event: HealEvent):
        """Player regenerating health or healed by someone."""

    @abc.abstractmethod
    def on_loot(self, event: LootEvent):
        """Player collecting loot/cubes."""

    @abc.abstractmethod
    def on_camp(self, event: CampEvent):
        """Player slipping into a bush."""

    @abc.abstractmethod
    def on_ambush(self, event: AmbushEvent):
        """Player launching an attack from a bush."""

    @abc.abstractmethod
    def on_poison_damage(self, event: PoisonDamageEvent):
        """Player takes damage from poison gas."""

    @abc.abstractmethod
    def on_poison_gas_start(self, event: PoisonGasStartEvent):
        """The poison gas has started entering the arena."""

    @abc.abstractmethod
    def on_poison_gas_coverage(self, event: PoisonGasCoverageEvent):
        """The poison gas has fully covered the map."""
