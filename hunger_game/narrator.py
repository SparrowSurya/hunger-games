"""
This module provides the match event narrator class:
* `EventNarrator`
* `Narration`
* `MatchNarrator`
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Callable, override, TYPE_CHECKING

from hunger_game.events import (
    MatchEventModel,
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
from hunger_game.observer import MatchObserver

if TYPE_CHECKING:
    from hunger_game.simulator import MatchSimulator


__all__ = (
    "EventNarrator",
    "MatchNarrator",
    "Narration",
)


class EventNarrator[M: MatchEventModel, T](abc.ABC):
    """Single event narrator."""

    @abc.abstractmethod
    def narrate(self, event: M) -> T:
        """Narrates the event."""


@dataclass(repr=False)
class Narration[T]:
    """Collection of narrations for match events."""

    match_begin: EventNarrator[MatchBeginEvent, T]
    match_end: EventNarrator[MatchEndEvent, T]
    moment_begin: EventNarrator[MomentBeginEvent, T]
    moment_end: EventNarrator[MomentEndEvent, T]
    attack: EventNarrator[AttackEvent, T]
    healing: EventNarrator[HealEvent, T]
    loot: EventNarrator[LootEvent, T]
    camp: EventNarrator[CampEvent, T]
    ambush: EventNarrator[AmbushEvent, T]
    poison_gas: EventNarrator[PoisonDamageEvent, T]
    gas_start: EventNarrator[PoisonGasStartEvent, T]
    gas_coverage: EventNarrator[PoisonGasCoverageEvent, T]


class MatchNarrator[T](MatchObserver):
    """Narrates the match.

    This helps to convert the each action into some kind of narration.
    """

    write: Callable[[T], None]
    narrations: Narration[T]

    def __init__(
        self,
        sim: MatchSimulator,
        narrations: Narration[T],
        writer: Callable[[T], None],
    ):
        MatchObserver.__init__(self, sim)
        self.narrations = narrations
        self.write = writer

    @override
    def on_match_begin(self, event: MatchBeginEvent):
        result = self.narrations.match_begin.narrate(event)
        self.write(result)

    @override
    def on_match_end(self, event: MatchEndEvent):
        result = self.narrations.match_end.narrate(event)
        self.write(result)

    @override
    def on_match_moment_begin(self, event: MomentBeginEvent):
        result = self.narrations.moment_begin.narrate(event)
        self.write(result)

    @override
    def on_match_moment_end(self, event: MomentEndEvent):
        result = self.narrations.moment_end.narrate(event)
        self.write(result)

    @override
    def on_attack(self, event: AttackEvent):
        result = self.narrations.attack.narrate(event)
        self.write(f"* {result}")  # type: ignore

    @override
    def on_heal(self, event: HealEvent):
        result = self.narrations.healing.narrate(event)
        self.write(f"* {result}")  # type: ignore

    @override
    def on_loot(self, event: LootEvent):
        result = self.narrations.loot.narrate(event)
        self.write(f"* {result}")  # type: ignore

    @override
    def on_camp(self, event: CampEvent):
        result = self.narrations.camp.narrate(event)
        self.write(f"* {result}")  # type: ignore

    @override
    def on_ambush(self, event: AmbushEvent):
        result = self.narrations.ambush.narrate(event)
        self.write(f"* {result}")  # type: ignore

    @override
    def on_poison_damage(self, event: PoisonDamageEvent):
        if event.silent:
            return
        result = self.narrations.poison_gas.narrate(event)
        self.write(f"  {result}")  # type: ignore

    @override
    def on_poison_gas_start(self, event: PoisonGasStartEvent):
        result = self.narrations.gas_start.narrate(event)
        self.write(f"\n{result}")  # type: ignore

    @override
    def on_poison_gas_coverage(self, event: PoisonGasCoverageEvent):
        result = self.narrations.gas_coverage.narrate(event)
        self.write(f"\n{result}")  # type: ignore
