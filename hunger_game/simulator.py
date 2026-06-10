"""
This module provides match simulator class:
* `MatchSimulator`
"""

from __future__ import annotations

import random
from typing import List, Callable, Dict, TYPE_CHECKING

from hunger_game.brawler import BrawlerAction, BrawlerNature
from hunger_game.game_mode import GameModeDynamic
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
    TeamupEvent,
    BetrayalEvent,
    PoisonGasStartEvent,
    PoisonGasCoverageEvent,
)
from hunger_game.match import (
    MatchState,
    MatchConfig,
    Encounter,
    EncounterState,
)
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
    encounter: List[Encounter]
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
        weights = player.state.action_weights.copy()
        alive_count = len(self._get_alive_players())
        total_players = len(self.state.players)
        ratio = alive_count / total_players

        gm_config = self.state.environment.config

        # Match Phase
        is_mid = gm_config.end_game_threshold < ratio <= gm_config.mid_game_threshold
        is_late = ratio <= gm_config.end_game_threshold

        # Apply Trait Modifiers (Multiplicative)
        for trait, intensity in player.traits:
            if trait == PlayerTrait.AGGRESSIVE:
                weights[BrawlerAction.ATTACK] *= 1.0 + (intensity * 4.0)
            elif trait == PlayerTrait.CAUTIOUS:
                weights[BrawlerAction.HEAL] *= 1.0 + (intensity * 4.0)
            elif trait == PlayerTrait.TEAMER:
                weights[BrawlerAction.TEAMUP] *= 1.0 + (intensity * 4.0)
            elif trait == PlayerTrait.BACKSTABBER:
                weights[BrawlerAction.BETRAY] *= 1.0 + (intensity * 4.0)
            elif trait == PlayerTrait.COLLECTOR:
                weights[BrawlerAction.LOOT] *= 1.0 + (intensity * 4.0)
            elif trait == PlayerTrait.CAMPER:
                weights[BrawlerAction.CAMP] *= 1.0 + (intensity * 4.0)
            elif trait == PlayerTrait.AMBUSER:
                weights[BrawlerAction.AMBUSH] *= 1.0 + (intensity * 4.0)

        # Apply Match Phase Bias
        if is_mid:
            weights[BrawlerAction.ATTACK] *= 1.3
        elif is_late:
            weights[BrawlerAction.ATTACK] *= 2.0
            weights[BrawlerAction.LOOT] *= 0.1
        else:
            # Early game: Boost looting and slight boost to aggression
            weights[BrawlerAction.LOOT] *= 2.0
            weights[BrawlerAction.ATTACK] *= 1.25

        # ENCOUNTER CONTEXT MODIFIERS
        allies = set()
        for alliance in encounter.alliances:
            if player.id in alliance:
                allies = alliance - {player.id}
                break

        non_allies = [
            p
            for p in encounter.participants
            if p.id != player.id and p.id not in allies
        ]

        if encounter.state == EncounterState.ISOLATED:
            # Cannot attack or teamup/betray if alone
            weights[BrawlerAction.ATTACK] = 0
            weights[BrawlerAction.TEAMUP] = 0
            weights[BrawlerAction.BETRAY] = 0
            # Higher chance to heal if damaged and alone
            if player.state.hp < player.max_hp:
                weights[BrawlerAction.HEAL] *= 2.0
        else:
            # If no non-allies, cannot attack or teamup
            if not non_allies:
                weights[BrawlerAction.ATTACK] = 0
                weights[BrawlerAction.TEAMUP] = 0
            # If no allies, cannot betray
            if not allies:
                weights[BrawlerAction.BETRAY] = 0

        # Prevent healing at full health
        if player.state.hp >= player.max_hp:
            weights[BrawlerAction.HEAL] = 0

        # Hardcore Rule: No healing after full poison coverage for non-support
        if gm_config.gas and self.moment >= gm_config.gas.full_coverage_at:
            if player.info.nature != BrawlerNature.SUPPORT:
                weights[BrawlerAction.HEAL] = 0

        # Final normalization
        items = list(weights.items())
        normalized = normalise_weights(items, lambda x: x[1], lambda x, w: (x[0], w))
        return dict(normalized)

    def _cleanup_encounters(self):
        """Removes dead players and dissolves/morphs empty or thin encounters."""
        for enc in self.state.encounters:
            enc.participants = [p for p in enc.participants if p.state.alive]

            # Clean up alliances
            alive_ids = {p.id for p in enc.participants}
            new_alliances = []
            for alliance in enc.alliances:
                cleaned_alliance = alliance & alive_ids
                if len(cleaned_alliance) >= 2:
                    new_alliances.append(cleaned_alliance)
            enc.alliances = new_alliances

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

    def _calculate_gas_damage(self) -> int:
        """Calculates current poison gas damage based on escalation."""
        gas_config = self.state.environment.config.gas
        if not gas_config:
            return 0

        if self.moment < gas_config.full_coverage_at:
            return gas_config.base_damage

        # Escalation after full coverage
        extra_moments = self.moment - gas_config.full_coverage_at
        damage = float(gas_config.base_damage)
        for _ in range(extra_moments):
            damage *= 1 + gas_config.scaling_factor

        return int(damage)

    def _apply_poison_gas(
        self, player: Player, action: BrawlerAction, encounter: Encounter
    ):
        """Calculates and applies poison gas damage contextually."""
        gas_config = self.state.environment.config.gas
        if (
            not gas_config
            or not player.state.alive
            or self.moment <= gas_config.safe_until
        ):
            return

        damage = self._calculate_gas_damage()
        hit = False
        context = "random"
        silent = False

        # Phase 1: Full Coverage
        if self.moment >= gas_config.full_coverage_at:
            hit = True
            context = "coverage"
            silent = True  # Suppress turn-by-turn narration in full coverage
        # Phase 2: Creeping Gas
        else:
            # Lazy Check
            if (
                action in [BrawlerAction.CAMP]
                or encounter.state == EncounterState.ISOLATED
            ):
                chance = gas_config.lazy_hit_chance

                # Passive trait penalty: Campers and Collectors are more likely to be hit by gas
                # if they don't have an offensive nature.
                passive_traits = {PlayerTrait.CAMPER, PlayerTrait.COLLECTOR}
                player_traits = {t[0] for t in player.traits}
                offensive_natures = {
                    BrawlerNature.DAMAGE_DEALER,
                    BrawlerNature.ASSASSIN,
                    BrawlerNature.TANK,
                    BrawlerNature.SNIPER,
                    BrawlerNature.ANTI_TANK,
                }

                if (
                    player_traits & passive_traits
                ) and player.info.nature not in offensive_natures:
                    chance *= 2.0

                if random.random() < chance:
                    hit = True
                    context = "lazy"
            # Cornered Check
            elif (
                player.state.hp / player.max_hp
                < gas_config.cornered_hp_threshold
            ):
                if random.random() < gas_config.cornered_hit_chance:
                    hit = True
                    context = "cornered"
            # Random Check
            elif random.random() < gas_config.random_hit_chance:
                hit = True
                context = "random"

        if hit:
            player.state.hp -= damage
            if not player.state.alive:
                self.state.eliminations.append((GameModeDynamic.POISON_GAS, player))
            self.observer.on_poison_damage(
                PoisonDamageEvent(player, damage, context, silent=silent)
            )

    def _calculate_damage(self, attacker: Player, target: Player) -> int:
        """Calculates damage with trait-based scaling and vulnerability."""
        gm_config = self.state.environment.config
        var = gm_config.damage_variance

        base_damage = random.randint(
            attacker.info.damage - var, attacker.info.damage + var
        )

        multiplier = 1.0

        # 0. Power Cube Bonus (10% per cube)
        multiplier += attacker.state.power_cubes * 0.1

        # 1. Aggressive Trait Bonus
        for trait, intensity in attacker.traits:
            if trait == PlayerTrait.AGGRESSIVE:
                multiplier *= 1.0 + (intensity * 0.5)

        # 2. Offensive Nature Bonus
        offensive_natures = {BrawlerNature.DAMAGE_DEALER, BrawlerNature.ASSASSIN}
        if attacker.info.nature in offensive_natures:
            multiplier *= 1.15

        # 3. Passive Vulnerability
        # Campers and Collectors take more damage from aggressive attackers if they lack offensive backup
        passive_traits = {PlayerTrait.CAMPER, PlayerTrait.COLLECTOR}
        target_traits = {t[0] for t in target.traits}
        attacker_traits = {t[0] for t in attacker.traits}

        if (PlayerTrait.AGGRESSIVE in attacker_traits) and (
            target_traits & passive_traits
        ):
            target_offensive_natures = {
                BrawlerNature.DAMAGE_DEALER,
                BrawlerNature.ASSASSIN,
                BrawlerNature.TANK,
                BrawlerNature.SNIPER,
                BrawlerNature.ANTI_TANK,
            }
            if target.info.nature not in target_offensive_natures:
                multiplier *= 1.2

        return int(base_damage * multiplier)

    async def run_moment(self):
        """Executes a single moment by processing localized encounters."""
        if len(self._get_alive_players()) <= 1:
            self._finished = True
            return

        self.observer.on_match_moment_begin(MomentBeginEvent(self.moment))
        alive_at_start = self._get_alive_players()

        # Phase 1: Spatial Management
        self._cleanup_encounters()
        self._matchmaker()

        # Phase 2: Action Resolution
        shuffled_encounters = self.state.encounters.copy()
        random.shuffle(shuffled_encounters)

        gm_config = self.state.environment.config

        for encounter in shuffled_encounters:
            participants = encounter.participants.copy()
            random.shuffle(participants)

            for player in participants:
                if not player.state.alive:
                    continue

                if len(self._get_alive_players()) <= 1:
                    break

                weights_dict = self._get_action_weights(player, encounter)
                action_types = list(weights_dict.keys())
                weights = list(weights_dict.values())

                if not any(weights):
                    # Even if wandering, they might take gas damage
                    self._apply_poison_gas(player, BrawlerAction.CAMP, encounter)
                    continue

                action = random.choices(action_types, weights=weights)[0]
                player.state.last_action = action

                if action == BrawlerAction.ATTACK:
                    allies = set()
                    for alliance in encounter.alliances:
                        if player.id in alliance:
                            allies = alliance
                            break

                    potential_targets = [
                        p
                        for p in encounter.participants
                        if p != player and p.id not in allies and p.state.alive
                    ]
                    if potential_targets:
                        target = random.choice(potential_targets)
                        damage = self._calculate_damage(player, target)
                        target.state.hp -= damage
                        if not target.state.alive:
                            self.state.eliminations.append((player, target))
                        self.observer.on_attack(AttackEvent(player, target, damage))

                        # Check if target is cornered into gas
                        self._apply_poison_gas(target, BrawlerAction.ATTACK, encounter)

                elif action == BrawlerAction.HEAL:
                    heal_amt = random.randint(gm_config.heal_min, gm_config.heal_max)
                    player.state.hp = min(
                        player.max_hp, player.state.hp + heal_amt
                    )
                    self.observer.on_heal(HealEvent(player, None))

                elif action == BrawlerAction.LOOT:
                    if random.random() < 0.5:  # 50% chance to find a cube
                        player.state.power_cubes += 1
                        # Small healing bonus for picking up a cube
                        player.state.hp = min(player.max_hp, player.state.hp + 400)
                        self.observer.on_loot(LootEvent(player))

                elif action == BrawlerAction.CAMP:
                    self.observer.on_camp(CampEvent(player))

                elif action == BrawlerAction.AMBUSH:
                    allies = set()
                    for alliance in encounter.alliances:
                        if player.id in alliance:
                            allies = alliance
                            break

                    potential_targets = [
                        p
                        for p in encounter.participants
                        if p != player and p.id not in allies and p.state.alive
                    ]
                    if potential_targets:
                        target = random.choice(potential_targets)
                        damage = self._calculate_damage(player, target)
                        target.state.hp -= damage
                        if not target.state.alive:
                            self.state.eliminations.append((player, target))
                        self.observer.on_ambush(AmbushEvent(player, target, damage))

                        self._apply_poison_gas(target, BrawlerAction.AMBUSH, encounter)

                elif action == BrawlerAction.TEAMUP:
                    allies = set()
                    for alliance in encounter.alliances:
                        if player.id in alliance:
                            allies = alliance
                            break

                    potential_targets = [
                        p
                        for p in encounter.participants
                        if p != player and p.id not in allies and p.state.alive
                    ]
                    if potential_targets:
                        target = random.choice(potential_targets)

                        # Decide response
                        target_traits = [t[0] for t in target.traits]
                        if (
                            PlayerTrait.TEAMER in target_traits
                            or PlayerTrait.BACKSTABBER in target_traits
                        ):
                            outcome = "ACCEPT"
                        else:
                            # 40% Accept, 40% Reject, 20% Attack
                            rand = random.random()
                            if rand < 0.4:
                                outcome = "ACCEPT"
                            elif rand < 0.8:
                                outcome = "REJECT"
                            else:
                                outcome = "ATTACK"

                        damage = 0
                        if outcome == "ACCEPT":
                            # Merge or create alliance
                            found_alliance = False
                            for alliance in encounter.alliances:
                                if target.id in alliance:
                                    alliance.add(player.id)
                                    found_alliance = True
                                    break

                            if not found_alliance:
                                encounter.alliances.append({player.id, target.id})

                        elif outcome == "ATTACK":
                            damage = self._calculate_damage(target, player)
                            player.state.hp -= damage
                            if not player.state.alive:
                                self.state.eliminations.append((target, player))

                        self.observer.on_teamup(
                            TeamupEvent(player, target, outcome, damage)
                        )
                        if damage > 0:
                            self._apply_poison_gas(
                                player, BrawlerAction.ATTACK, encounter
                            )

                elif action == BrawlerAction.BETRAY:
                    alliance_index = -1
                    allies_list = []
                    for i, alliance in enumerate(encounter.alliances):
                        if player.id in alliance:
                            alliance_index = i
                            allies_list = [
                                p
                                for p in encounter.participants
                                if p.id in alliance and p.id != player.id
                            ]
                            break

                    if allies_list:
                        target = random.choice(allies_list)
                        # Backstab damage (2x base)
                        damage = self._calculate_damage(player, target) * 2
                        target.state.hp -= damage
                        if not target.state.alive:
                            self.state.eliminations.append((player, target))

                        # Break alliance (remove player from set)
                        encounter.alliances[alliance_index].remove(player.id)
                        if len(encounter.alliances[alliance_index]) < 2:
                            encounter.alliances.pop(alliance_index)

                        self.observer.on_betrayal(BetrayalEvent(player, target, damage))

                # Actor might take gas damage regardless of action
                self._apply_poison_gas(player, action, encounter)

            encounter.age += 1

        alive_at_end = self._get_alive_players()
        eliminated_this_moment = [p for p in alive_at_start if p not in alive_at_end]

        self.observer.on_match_moment_end(
            MomentEndEvent(len(alive_at_end), eliminated_this_moment)
        )

        # Trigger gas announcements for the upcoming moment
        gas_config = self.state.environment.config.gas
        if gas_config:
            if self.moment == gas_config.safe_until:
                self.observer.on_poison_gas_start(PoisonGasStartEvent())
            elif self.moment == gas_config.full_coverage_at - 1:
                self.observer.on_poison_gas_coverage(PoisonGasCoverageEvent())

        self.moment += 1

    async def run(self):
        """Executes a complete match."""
        self.observer.on_match_begin(MatchBeginEvent(self.state))
        while not self._finished and len(self._get_alive_players()) > 1:
            await self.run_moment()

        winner = self._get_alive_players()[0] if self._get_alive_players() else None
        self.observer.on_match_end(MatchEndEvent(self.state, winner))
