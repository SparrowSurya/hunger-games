"""
This module provides the match event narrator class:
* `EventNarrator`
* `Narration`
* `MatchNarrator`
"""


from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import List, Tuple, Any, Callable, override, TYPE_CHECKING

from hunger_game.observer import MatchObserver
from hunger_game.player import Player
from hunger_game.game_mode import Collectable

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
    attack: EventNarrator[T]
    bush_camp: EventNarrator[T]
    healing: EventNarrator[T]
    teamup: EventNarrator[T]
    collect: EventNarrator[T]
    hiding: EventNarrator[T]
    betray: EventNarrator[T]
    poison_gas: EventNarrator[T]


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
    def nothing(self, moment: int):
        pass

    @override
    def attack(self, attacker: Player, target: Player, damage: int, collect: Tuple[Collectable, int] | None):
        result = self.narrations.attack.narrate(attacker, target, damage, collect)
        self.write(result)

    @override
    def bush_camp(self, camper: Player):
        result = self.narrations.bush_camp.narrate(camper)
        self.write(result)

    @override
    def heal(self, healed: Player, healer: Player | None):
        result = self.narrations.healing.narrate(healed, healer)
        self.write(result)

    @override
    def teamup(self, source: Player, target: Player, teamed: bool):
        result = self.narrations.teamup.narrate(source, target, teamed)
        self.write(result)

    @override
    def collect(self, collector: Player, item: Collectable):
        result = self.narrations.collect.narrate(collector, item)
        self.write(result)

    @override
    def stay_hidden(self, hider: Player):
        result = self.narrations.hiding.narrate(hider)
        self.write(result)

    @override
    def betray(self, betrayer: Player, betrayed: Player, damage: int):
        result = self.narrations.betray.narrate(betrayer, betrayed, damage)
        self.write(result)

    @override
    def poison_gas_closing(self, damaged: List[Tuple[Player, int]]):
        result = self.narrations.poison_gas.narrate(damaged)
        self.write(result)
