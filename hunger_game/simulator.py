"""
This module provides match simulator class:
* `MatchSimulator`
"""


import asyncio
import random
from typing import List, Tuple, Callable

from hunger_game.brawler import BrawlerAction
from hunger_game.game_mode import Collectable, GameModeDynamic
from hunger_game.match import MatchState
from hunger_game.observer import MatchObserver
from hunger_game.player import Player


__all__ = (
    "MatchSimulator",
)


class MatchSimulator:
    """Simulates the match.

    This controles the overall events happening and decisions taken each moments. It also
    manages the moments and passing it to the observer.
    """

    observer: MatchObserver
    state: MatchState
    moment: int
    _finished: bool

    def __init__(
        self,
        observer_factory: Callable[[MatchSimulator], MatchObserver],
        state: MatchState,
    ):
        self.observer = observer_factory(self)
        self.state = state
        self.moment = 1
        self._finished = False

    def _get_alive_players(self) -> List[Player]:
        return [p for p in self.state.players if p.state.alive]

    async def run_moment(self):
        """Executes a single moment in the match."""
        alive = self._get_alive_players()
        if len(alive) <= 1:
            self._finished = True
            return

        self.observer.match_moment_begin(self.moment)
        random.shuffle(alive)

        for player in alive:
            if not player.state.alive:
                continue

            if len(self._get_alive_players()) <= 1:
                break

            action_types = list(player.info.actions.keys())
            weights = list(player.info.actions.values())
            action = random.choices(action_types, weights=weights)[0]

            if action == BrawlerAction.NOTHING:
                pass
            elif action == BrawlerAction.ATTACK:
                targets = [p for p in self._get_alive_players() if p != player]
                if targets:
                    target = random.choice(targets)
                    damage = random.randint(player.info.damage - 5, player.info.damage + 5)
                    target.state.hp -= damage
                    collect = None
                    if not target.state.alive:
                        self.state.eliminations.append((player, target))
                        cubes = (target.state.cubes // 2) + 1
                        player.state.cubes += cubes
                        collect = (Collectable.CUBE, cubes)
                    self.observer.attack(player, target, damage, collect)
            elif action == BrawlerAction.BUSH_CAMP:
                player.state.hidden = True
                self.observer.bush_camp(player)
            elif action == BrawlerAction.HEAL:
                player.state.hidden = False
                heal_amt = random.randint(10, 25)
                player.state.hp = min(player.info.hitpoionts, player.state.hp + heal_amt)
                self.observer.heal(player, None)
            elif action == BrawlerAction.TEAM_UP:
                targets = [p for p in self._get_alive_players() if p != player]
                if targets:
                    target = random.choice(targets)
                    success = random.random() < 0.3
                    self.observer.teamup(player, target, success)
            elif action == BrawlerAction.COLLECT:
                player.state.hidden = False
                player.state.cubes += 1
                self.observer.collect(player, Collectable.CUBE)
            elif action == BrawlerAction.STAY_HIDDEN:
                if player.state.hidden:
                    self.observer.stay_hidden(player)
                else:
                    player.state.hidden = True
                    self.observer.bush_camp(player)
            elif action == BrawlerAction.BETRAY:
                targets = [p for p in self._get_alive_players() if p != player]
                if targets:
                    target = random.choice(targets)
                    damage = player.info.damage + 10
                    target.state.hp -= damage
                    if not target.state.alive:
                        self.state.eliminations.append((player, target))
                    self.observer.betray(player, target, damage)

            await asyncio.sleep(0.1)

        if GameModeDynamic.POISON_GAS in self.state.environment.dynamics:
            if self.moment % 3 == 0:
                damaged: List[Tuple[Player, int]] = []
                dmg = 15
                for p in self._get_alive_players():
                    if random.random() < 0.2:
                        p.state.hp -= dmg
                        damaged.append((p, dmg))
                if damaged:
                    self.observer.poison_gas_closing(damaged)

        self.moment += 1

    async def run(self):
        """Executes a complete match."""
        self.observer.match_begin()
        while not self._finished and len(self._get_alive_players()) > 1:
            await self.run_moment()

        winner = self._get_alive_players()[0] if self._get_alive_players() else None
        self.observer.match_end(winner)
