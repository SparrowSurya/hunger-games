"""
This module provides the match event narrator class:
* `EventNarrator`
* `Narration`
* `MatchNarrator`
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Callable, override, TYPE_CHECKING

from hunger_game.observer import MatchObserver
from hunger_game.player import Player

if TYPE_CHECKING:
    from hunger_game.simulator import MatchSimulator


__all__ = (
    "EventNarrator",
    "MatchNarrator",
    "Narration",
)


class EventNarrator[T](abc.ABC):
    """Single event narrator."""

    @abc.abstractmethod
    def narrate(self, *args: Any, **kwargs: Any) -> T:
        """Narrates the event."""


@dataclass(repr=False)
class Narration[T]:
    """Collection of narrations for match events."""

    match_begin: EventNarrator[T]
    match_end: EventNarrator[T]
    moment_begin: EventNarrator[T]
    moment_end: EventNarrator[T]
    attack: EventNarrator[T]
    healing: EventNarrator[T]
    loot: EventNarrator[T]
    camp: EventNarrator[T]
    ambush: EventNarrator[T]
    poison_gas: EventNarrator[T]
    gas_coverage: EventNarrator[T]


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
    def match_begin(self):
        result = self.narrations.match_begin.narrate(self.sim.state)
        self.write(result)

    @override
    def match_end(self, winner: Player | None):
        result = self.narrations.match_end.narrate(self.sim.state, winner)
        self.write(result)

    @override
    def match_moment_begin(self, moment: int):
        result = self.narrations.moment_begin.narrate(moment)
        self.write(result)

    @override
    def match_moment_end(self, alive_count: int, eliminated: list[Player]):
        result = self.narrations.moment_end.narrate(alive_count, eliminated)
        self.write(result)

    @override
    def attack(self, attacker: Player, target: Player, damage: int):
        result = self.narrations.attack.narrate(attacker, target, damage)
        self.write(f"* {result}")  # type: ignore

    @override
    def heal(self, healed: Player, healer: Player | None):
        result = self.narrations.healing.narrate(healed, healer)
        self.write(f"* {result}")  # type: ignore

    @override
    def loot(self, player: Player):
        result = self.narrations.loot.narrate(player)
        self.write(f"* {result}")  # type: ignore

    @override
    def camp(self, player: Player):
        result = self.narrations.camp.narrate(player)
        self.write(f"* {result}")  # type: ignore

    @override
    def ambush(self, attacker: Player, target: Player, damage: int):
        result = self.narrations.ambush.narrate(attacker, target, damage)
        self.write(f"* {result}")  # type: ignore

    @override
    def poison_damage(
        self, player: Player, damage: int, context: str, silent: bool = False
    ):
        if silent:
            return
        result = self.narrations.poison_gas.narrate(player, damage, context)
        self.write(f"  {result}")  # type: ignore

    @override
    def poison_gas_coverage(self):
        result = self.narrations.gas_coverage.narrate()
        self.write(f"\n{result}")  # type: ignore
