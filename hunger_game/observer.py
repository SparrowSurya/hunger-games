"""
This module provide match observer class:
* `MatchObserver`
"""


from __future__ import annotations
import abc
from typing import List, Tuple, TYPE_CHECKING

from hunger_game.game_mode import Collectable
from hunger_game.player import Player

if TYPE_CHECKING:
    from hunger_game.simulator import MatchSimulator


__all__ = (
    "MatchObserver",
)


class MatchObserver(abc.ABC):
    """Observes the events in the match.

    This helps to observe the events happening in match which can be further passed to
    narrator for event narration.
    """

    sim: MatchSimulator

    def __init__(self, simulator: MatchSimulator):
        self.sim = simulator

    @abc.abstractmethod
    def match_begin(self):
        """Match start event."""

    @abc.abstractmethod
    def match_end(self, winner: Player | None):
        """Match end event.

        :Args:
        * winner - winner of the match or `None` if draw.
        """

    @abc.abstractmethod
    def match_moment_begin(self, moment: int):
        """Match moment beginning.

        :Args:
        * moment - moment serial number.
        """

    @abc.abstractmethod
    def nothing(self, moment: int):
        """Match moment ending.

        :Args:
        * moment - moment serial number.
        """

    @abc.abstractmethod
    def attack(self, attacker: Player, target: Player, damage: int, collect: Tuple[Collectable, int] | None):
        """Player attacks someone.

        :Args:
        * attacker - player attacking.
        * target - player taking damage.
        * damage - damage dealt.
        * collect - item collected as `(item, count)`.
        """

    @abc.abstractmethod
    def bush_camp(self, camper: Player):
        """Player bush camping.

        :Args:
        * capmer - camping player.
        """

    @abc.abstractmethod
    def heal(self, healed: Player, healer: Player | None):
        """Player regenerating health or healed by someone.

        :Args:
        * healed - player who gets the healing.
        * healer - player who healed, `None` if player regenrating health.
        """

    @abc.abstractmethod
    def teamup(self, source: Player, target: Player, teamed: bool):
        """Player trying to teamup with enemy.

        :Args:
        * source - player initiated the teamup by spinning.
        * target - player with whom teaup was to happen.
        * teamed - result of spinning.
        """

    @abc.abstractmethod
    def collect(self, collector: Player, item: Collectable):
        """Player opening box.

        :Args:
        * collector - playing collecting something.
        * item - collectable item.
        """

    @abc.abstractmethod
    def stay_hidden(self, hider: Player):
        """Player still hiding in bush.

        :Args:
        * hider - player hiding.
        """

    @abc.abstractmethod
    def betray(self, betrayer: Player, betrayed: Player, damage: int):
        """Player betraying teamed enemy.

        :Args:
        * betrayer - player betrayed its teamup.
        * betrayed - player who got betrayed.
        * damage - damage given by betrayer to betrayed.
        """

    @abc.abstractmethod
    def poison_gas_closing(self, damaged: List[Tuple[Player, int]]):
        """Poison gas closing in.

        :Args:
        * damaged - players damaged by poison with the damage taken.
        """
