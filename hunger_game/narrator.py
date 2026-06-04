"""
This module provides the match event narrator class:
* `EventNarrator`
* `MatchNarrator`
"""


from __future__ import annotations

import abc
from typing import Dict, List, Tuple, Any, Callable, override, TYPE_CHECKING

from hunger_game.match import MatchEvent
from hunger_game.observer import MatchObserver
from hunger_game.player import Player
from hunger_game.game_mode import Collectable

if TYPE_CHECKING:
    from hunger_game.simulator import MatchSimulator


__all__ = (
    "EventNarrator",
    "MatchNarrator",
)


class EventNarrator[T](abc.ABC):
    """Single event narrator."""

    @abc.abstractmethod
    def narrate(self, **kwargs: Dict[str, Any]) -> T:
        """Narrates the event."""


class MatchNarrator[T](MatchObserver):
    """Narrates the match.

    This helps to convert the each action into some kind of narration.
    """

    write: Callable[[T], None]
    narrations: Dict[MatchEvent, EventNarrator[T]]

    def __init__(
        self,
        sim: MatchSimulator,
        narrations: Dict[MatchEvent, EventNarrator[T]],
        writer: Callable[[T], None],
    ):
        MatchObserver.__init__(self, sim)
        self.narrations = narrations
        self.write = writer

    def narrator(self, event: MatchEvent) -> EventNarrator[T]:
        return self.narrations[event]

    @override
    def match_begin(self):
        narrator = self.narrator(MatchEvent.MATCH_BEGIN)
        result = narrator.narrate(state=self.sim.state) # type: ignore
        self.write(result)

    @override
    def match_end(self, winner: Player | None):
        narrator = self.narrator(MatchEvent.MATCH_END)
        result = narrator.narrate(state=self.sim.state, winner=winner) # type: ignore
        self.write(result)

    @override
    def match_moment_begin(self, moment: int):
        narrator = self.narrator(MatchEvent.MOMENT_BEGIN)
        result = narrator.narrate(moment=moment) # type: ignore
        self.write(result)

    @override
    def nothing(self, moment: int):
        pass

    @override
    def attack(self, attacker: Player, target: Player, damage: int, collect: Tuple[Collectable, int] | None):
        narrator = self.narrator(MatchEvent.ATTACK)
        result = narrator.narrate(attacker=attacker, target=target, damage=damage, collect=collect) # type: ignore
        self.write(result)

    @override
    def bush_camp(self, camper: Player):
        narrator = self.narrator(MatchEvent.BUSH_CAMP)
        result = narrator.narrate(camper=camper) # type: ignore
        self.write(result)

    @override
    def heal(self, healed: Player, healer: Player | None):
        narrator = self.narrator(MatchEvent.HEALING)
        result = narrator.narrate(healed=healed, healer=healer) # type: ignore
        self.write(result)

    @override
    def teamup(self, source: Player, target: Player, teamed: bool):
        narrator = self.narrator(MatchEvent.TEAMUP)
        result = narrator.narrate(source=source, target=target, teamed=teamed) # type: ignore
        self.write(result)

    @override
    def collect(self, collector: Player, item: Collectable):
        narrator = self.narrator(MatchEvent.COLLECT)
        result = narrator.narrate(collector=collector, item=item) # type: ignore
        self.write(result)

    @override
    def stay_hidden(self, hider: Player):
        narrator = self.narrator(MatchEvent.HIDING)
        result = narrator.narrate(hider=hider) # type: ignore
        self.write(result)

    @override
    def betray(self, betrayer: Player, betrayed: Player, damage: int):
        narrator = self.narrator(MatchEvent.BETRAY)
        result = narrator.narrate(betrayer=betrayer, betrayed=betrayed, damage=damage) # type: ignore
        self.write(result)

    @override
    def poison_gas_closing(self, damaged: List[Tuple[Player, int]]):
        narrator = self.narrator(MatchEvent.POSION_GAS)
        result = narrator.narrate(damaged=damaged) # type: ignore
        self.write(result)
