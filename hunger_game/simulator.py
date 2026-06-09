"""
This module provides match simulator class:
* `MatchSimulator`
"""

from __future__ import annotations

import asyncio
import random
from typing import List, Tuple, Callable, Dict, TYPE_CHECKING

from hunger_game.brawler import BrawlerAction
from hunger_game.game_mode import GameModeDynamic
from hunger_game.match import MatchState, MatchConfig, Encounter, EncounterState
from hunger_game.player import Player, PlayerTrait
from hunger_game.utils import normalise_weights

if TYPE_CHECKING:
    from hunger_game.observer import MatchObserver


__all__ = ("MatchSimulator",)


class MatchSimulator:
    """Simulates the match using a stateful encounter system.

    This controls localized skirmishes and interactions between players,
    simulating realistic spatial dynamics and engagement morphing.
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

        # Initial setup: Put all players in ISOLATED encounters
        if not self.state.encounters:
            for player in self.state.players:
                self.state.encounters.append(
                    Encounter(participants=[player], state=EncounterState.ISOLATED)
                )

    def _get_alive_players(self) -> List[Player]:
        return [p for p in self.state.players if p.state.alive]

    def _get_action_weights(
        self, player: Player, encounter: Encounter
    ) -> Dict[BrawlerAction, float]:
        """Calculates dynamic action weights based on traits, phase, and encounter context."""
        weights = player.info.actions.copy()
        alive_count = len(self._get_alive_players())
        total_players = len(self.state.players)
        ratio = alive_count / total_players

        gm_config = self.state.environment.config

        # Match Phase
        is_mid = gm_config.end_game_threshold < ratio <= gm_config.mid_game_threshold
        is_late = ratio <= gm_config.end_game_threshold

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

        # ENCOUNTER CONTEXT MODIFIERS
        if encounter.state == EncounterState.ISOLATED:
            # Cannot attack if alone
            weights[BrawlerAction.ATTACK] = 0
            # Higher chance to heal if damaged and alone
            if player.state.hp < player.info.hitpoints:
                weights[BrawlerAction.HEAL] *= 2.0

        # Prevent healing at full health
        if player.state.hp >= player.info.hitpoints:
            weights[BrawlerAction.HEAL] = 0

        # Final normalization
        items = list(weights.items())
        normalized = normalise_weights(items, lambda x: x[1], lambda x, w: (x[0], w))
        return dict(normalized)

    def _cleanup_encounters(self):
        """Removes dead players and dissolves/morphs empty or thin encounters."""
        for enc in self.state.encounters:
            enc.participants = [p for p in enc.participants if p.state.alive]

        # Filter out empty encounters
        self.state.encounters = [
            enc for enc in self.state.encounters if enc.participants
        ]

        # Morph thin encounters
        for enc in self.state.encounters:
            count = len(enc.participants)
            if count == 1:
                enc.state = EncounterState.ISOLATED
            elif count == 2:
                enc.state = EncounterState.DUEL
            else:
                enc.state = EncounterState.MELEE

    def _matchmaker(self):
        """Merges isolated players or adds them to existing skirmishes."""
        isolated = [
            enc for enc in self.state.encounters if enc.state == EncounterState.ISOLATED
        ]
        random.shuffle(isolated)

        # 1. Merge Isolated into Duels
        while len(isolated) >= 2:
            if random.random() < self.config.encounter_merge_chance:
                enc1 = isolated.pop()
                enc2 = isolated.pop()
                enc1.participants.extend(enc2.participants)
                enc1.state = EncounterState.DUEL
                self.state.encounters.remove(enc2)
            else:
                # Still isolated this turn
                isolated.pop()

        # 2. Third-Partying: Remaining Isolated might join existing DUELs
        skirmishes = [
            enc
            for enc in self.state.encounters
            if enc.state in [EncounterState.DUEL, EncounterState.MELEE]
        ]
        if isolated and skirmishes:
            for iso_enc in isolated[:]:
                if random.random() < self.config.third_party_chance:
                    target_skirmish = random.choice(skirmishes)
                    target_skirmish.participants.extend(iso_enc.participants)
                    target_skirmish.state = EncounterState.MELEE
                    self.state.encounters.remove(iso_enc)
                    isolated.remove(iso_enc)

    async def run_moment(self):
        """Executes a single moment by processing localized encounters."""
        if len(self._get_alive_players()) <= 1:
            self._finished = True
            return

        self.observer.match_moment_begin(self.moment)

        # Phase 1: Spatial Management
        self._cleanup_encounters()
        self._matchmaker()

        # Phase 2: Action Resolution
        # We shuffle encounters and participants to ensure fairness
        shuffled_encounters = self.state.encounters.copy()
        random.shuffle(shuffled_encounters)

        gm_config = self.state.environment.config

        for encounter in shuffled_encounters:
            participants = encounter.participants.copy()
            random.shuffle(participants)

            for player in participants:
                if not player.state.alive:
                    continue

                # Player might have won the match during this loop
                if len(self._get_alive_players()) <= 1:
                    break

                weights_dict = self._get_action_weights(player, encounter)
                action_types = list(weights_dict.keys())
                weights = list(weights_dict.values())

                # If no weights (e.g. isolated and full HP), they just wander (do nothing)
                if not any(weights):
                    continue

                action = random.choices(action_types, weights=weights)[0]

                if action == BrawlerAction.ATTACK:
                    # Targets can only be other participants in the same encounter
                    potential_targets = [
                        p
                        for p in encounter.participants
                        if p != player and p.state.alive
                    ]
                    if potential_targets:
                        target = random.choice(potential_targets)
                        var = gm_config.damage_variance
                        damage = random.randint(
                            player.info.damage - var, player.info.damage + var
                        )
                        target.state.hp -= damage
                        if not target.state.alive:
                            self.state.eliminations.append((player, target))
                        self.observer.attack(player, target, damage)

                elif action == BrawlerAction.HEAL:
                    heal_amt = random.randint(gm_config.heal_min, gm_config.heal_max)
                    player.state.hp = min(
                        player.info.hitpoints, player.state.hp + heal_amt
                    )
                    self.observer.heal(player, None)

                await asyncio.sleep(0.05)

            encounter.age += 1

        # Poison Gas Logic (Independent of localized encounters)
        if GameModeDynamic.POISON_GAS in self.state.environment.dynamics:
            gm_config = self.state.environment.config
            is_escalated = (
                self.gas_iterations >= gm_config.gas_escalation_after_iterations
            )
            frequency = 1 if is_escalated else gm_config.gas_initial_frequency

            if self.moment % frequency == 0:
                self.gas_iterations += 1
                damaged: List[Tuple[Player, int]] = []
                hit_chance = (
                    gm_config.gas_escalated_hit_chance
                    if is_escalated
                    else gm_config.gas_hit_chance
                )

                for p in self._get_alive_players():
                    if random.random() < hit_chance:
                        p.state.hp -= gm_config.gas_damage
                        damaged.append((p, gm_config.gas_damage))
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
