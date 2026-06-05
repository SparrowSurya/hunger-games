"""
This module provides match simulator class:
* `MatchSimulator`
"""

from __future__ import annotations

import asyncio
import random
from typing import List, Tuple, Callable, Dict, TYPE_CHECKING

from hunger_game.brawler import BrawlerAction, BrawlerEngagement
from hunger_game.game_mode import GameModeDynamic
from hunger_game.match import MatchState, MatchConfig
from hunger_game.player import Player, PlayerTrait
from hunger_game.utils import normalise_weights

if TYPE_CHECKING:
    from hunger_game.observer import MatchObserver


__all__ = ("MatchSimulator",)


class MatchSimulator:
    """Simulates the match.

    This controls the overall events happening and decisions taken each moments. It also
    manages the moments and passing it to the observer.
    """

    observer: MatchObserver
    state: MatchState
    config: MatchConfig
    moment: int
    gas_iterations: int
    _finished: bool

    def __init__(
        self,
        observer_factory: Callable[[MatchSimulator], MatchObserver],
        state: MatchState,
        config: MatchConfig,
    ):
        self.observer = observer_factory(self)
        self.state = state
        self.config = config
        self.moment = 1
        self.gas_iterations = 0
        self._finished = False

    def _get_alive_players(self) -> List[Player]:
        return [p for p in self.state.players if p.state.alive]

    def _get_action_weights(self, player: Player) -> Dict[BrawlerAction, float]:
        """Calculates dynamic action weights based on traits and match state."""
        weights = player.info.actions.copy()
        alive_count = len(self._get_alive_players())
        total_players = len(self.state.players)
        ratio = alive_count / total_players

        # Determine Match Phase
        is_mid = (
            self.config.end_game_threshold < ratio <= self.config.mid_game_threshold
        )
        is_late = ratio <= self.config.end_game_threshold

        # Apply Trait Modifiers
        for trait, intensity in player.traits:
            if trait == PlayerTrait.AGGRESSIVE:
                weights[BrawlerAction.ATTACK] += intensity * 0.2
            elif trait == PlayerTrait.CAUTIOUS:
                weights[BrawlerAction.HEAL] += intensity * 0.2

        # Apply Match Phase Bias
        if is_mid:
            weights[BrawlerAction.ATTACK] *= 1.3
        elif is_late:
            weights[BrawlerAction.ATTACK] *= 2.0

        # Final normalization
        items = list(weights.items())
        normalized = normalise_weights(items, lambda x: x[1], lambda x, w: (x[0], w))
        return dict(normalized)

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

            # Use dynamic weights based on traits and match phase
            weights_dict = self._get_action_weights(player)
            action_types = list(weights_dict.keys())
            weights = list(weights_dict.values())
            action = random.choices(action_types, weights=weights)[0]

            if action == BrawlerAction.ATTACK:
                player.state.engagement = BrawlerEngagement.EXPOSED
                targets = [p for p in self._get_alive_players() if p != player]
                if targets:
                    target = random.choice(targets)
                    var = self.config.damage_variance
                    damage = random.randint(
                        player.info.damage - var, player.info.damage + var
                    )
                    target.state.hp -= damage
                    if not target.state.alive:
                        self.state.eliminations.append((player, target))
                    self.observer.attack(player, target, damage)
            elif action == BrawlerAction.HEAL:
                player.state.engagement = BrawlerEngagement.HEALING
                heal_amt = random.randint(self.config.heal_min, self.config.heal_max)
                player.state.hp = min(player.info.hitpoints, player.state.hp + heal_amt)
                self.observer.heal(player, None)

            await asyncio.sleep(0.1)

        # Poison Gas Logic
        if GameModeDynamic.POISON_GAS in self.state.environment.dynamics:
            is_escalated = (
                self.gas_iterations >= self.config.gas_escalation_after_iterations
            )
            frequency = 1 if is_escalated else self.config.gas_initial_frequency

            if self.moment % frequency == 0:
                self.gas_iterations += 1
                damaged: List[Tuple[Player, int]] = []
                hit_chance = (
                    self.config.gas_escalated_hit_chance
                    if is_escalated
                    else self.config.gas_hit_chance
                )

                for p in self._get_alive_players():
                    if random.random() < hit_chance:
                        p.state.hp -= self.config.gas_damage
                        damaged.append((p, self.config.gas_damage))
                        if not p.state.alive:
                            self.state.eliminations.append(
                                (GameModeDynamic.POISON_GAS, p)
                            )

                self.observer.poison_gas_closing(damaged)

        self.observer.match_moment_end(len(self._get_alive_players()))
        self.moment += 1

    async def run(self):
        """Executes a complete match."""
        self.observer.match_begin()
        while not self._finished and len(self._get_alive_players()) > 1:
            await self.run_moment()

        winner = self._get_alive_players()[0] if self._get_alive_players() else None
        self.observer.match_end(winner)
