"""
This module provide match observer class:
* `MatchObserver`
"""


from __future__ import annotations
import abc
from typing import List, Tuple, TYPE_CHECKING

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
    def match_moment_end(self, alive_count: int):
        """Match moment ending.

        :Args:
        * alive_count - number of players still alive.
        """

    @abc.abstractmethod
    def attack(self, attacker: Player, target: Player, damage: int):
        """Player attacks someone.

        :Args:
        * attacker - player attacking.
        * target - player taking damage.
        * damage - damage dealt.
        """

    @abc.abstractmethod
    def heal(self, healed: Player, healer: Player | None):
        """Player regenerating health or healed by someone.

        :Args:
        * healed - player who gets the healing.
        * healer - player who healed, `None` if player regenrating health.
        """

    @abc.abstractmethod
    def poison_gas_closing(self, damaged: List[Tuple[Player, int]]):
        """Poison gas closing in.

        :Args:
        * damaged - players damaged by poison with the damage taken.
        """
