"""
This modules provides narration engine:
* `NarrationEngine`
* `TextNarrationEngine`
"""

from __future__ import annotations

import abc
import random
from enum import StrEnum
from typing import Any, Dict, TYPE_CHECKING

from hunger_game.brawler import BrawlerAction
from hunger_game.player import PlayerTrait

if TYPE_CHECKING:
    from hunger_game.player import Player
    from hunger_game.match import MatchConfig


__all__ = (
    "NarrationEngine",
    "TextNarrationEngine",
)


class NarrationComponent(StrEnum):
    """Internal keys for narration data structure."""

    INTROS = "intros"
    VERBS = "verbs"
    OUTROS = "outros"


class NarrationMood(StrEnum):
    """Moods used to select intros."""

    AGGRESSIVE = "AGGRESSIVE"
    CAUTIOUS = "CAUTIOUS"
    DESPERATE = "DESPERATE"
    NEUTRAL = "NEUTRAL"
    SNEAKY = "SNEAKY"


class NarrationMagnitude(StrEnum):
    """Magnitude of an action's result."""

    MINOR = "MINOR"
    MAJOR = "MAJOR"
    ELIMINATION = "ELIMINATION"


class NarrationFallback(StrEnum):
    """Fallback keys for narration lookups."""

    DEFAULT = "DEFAULT"


class NarrationEngine[T](abc.ABC):
    """Base narration engine class."""

    @abc.abstractmethod
    def narrate_attack(self, attacker: Player, target: Player, damage: int) -> T:
        """Narrates an attack."""

    @abc.abstractmethod
    def narrate_heal(self, player: Player) -> T:
        """Narrates a healing event."""

    @abc.abstractmethod
    def narrate_loot(self, player: Player) -> T:
        """Narrates a looting event."""

    @abc.abstractmethod
    def narrate_camp(self, player: Player) -> T:
        """Narrates a camping event."""

    @abc.abstractmethod
    def narrate_ambush(self, attacker: Player, target: Player, damage: int) -> T:
        """Narrates an ambush."""


class TextNarrationEngine(NarrationEngine[str]):
    """Text based narration engine class."""

    data: Dict[str, Any]
    config: MatchConfig

    def __init__(self, data: Dict[str, Any], config: MatchConfig):
        self.data = data
        self.config = config

    def _get_mood(self, player: Player) -> NarrationMood:
        """Determines the mood of the player for narration."""
        # Special Case: If last action was CAMP, they might be SNEAKY
        if player.state.last_action == BrawlerAction.CAMP:
            return NarrationMood.SNEAKY

        hp_ratio = player.state.hp / player.info.hitpoints

        if hp_ratio < 0.3:
            return NarrationMood.DESPERATE

        # Check traits
        traits = [t[0] for t in player.traits]
        if PlayerTrait.AGGRESSIVE in traits:
            return NarrationMood.AGGRESSIVE
        if PlayerTrait.CAUTIOUS in traits:
            return NarrationMood.CAUTIOUS

        return NarrationMood.NEUTRAL

    def _get_verb(self, action: BrawlerAction, nature: str) -> str:
        """Picks a random verb based on action and brawler nature."""
        action_verbs = self.data[NarrationComponent.VERBS].get(action.name, {})

        default_pool = action_verbs.get(NarrationFallback.DEFAULT, ["acts"])
        nature_pool = action_verbs.get(nature, [])

        if not nature_pool:
            return random.choice(default_pool)

        pools = [default_pool, nature_pool]
        weights = [1.5, 1.0]

        chosen_pool = random.choices(pools, weights=weights, k=1)[0]
        return random.choice(chosen_pool)

    def _get_outro(
        self, action: BrawlerAction, magnitude: NarrationMagnitude | NarrationFallback
    ) -> str:
        """Picks a random outro based on action and result magnitude."""
        action_outros = self.data[NarrationComponent.OUTROS].get(action.name, {})
        outro_pool = action_outros.get(
            magnitude, action_outros.get(NarrationFallback.DEFAULT, [""])
        )
        return random.choice(outro_pool)

    def _get_intro(self, player: Player) -> str:
        """Randomly picks an intro based on configuration frequency."""
        # Ambush always uses a sneaky intro
        if player.state.last_action == BrawlerAction.CAMP:
            mood = NarrationMood.SNEAKY
        elif random.random() > self.config.intro_frequency:
            return ""
        else:
            mood = self._get_mood(player)

        intro_pool = self.data[NarrationComponent.INTROS].get(
            mood, self.data[NarrationComponent.INTROS][NarrationMood.NEUTRAL]
        )
        return random.choice(intro_pool)

    def narrate_attack(self, attacker: Player, target: Player, damage: int) -> str:
        intro = self._get_intro(attacker)
        verb = self._get_verb(BrawlerAction.ATTACK, attacker.info.nature)

        if not target.state.alive:
            magnitude = NarrationMagnitude.ELIMINATION
        elif damage > (target.info.hitpoints * 0.3):
            magnitude = NarrationMagnitude.MAJOR
        else:
            magnitude = NarrationMagnitude.MINOR

        outro = self._get_outro(BrawlerAction.ATTACK, magnitude)
        return self._assemble(intro, attacker.info.name, verb, target.info.name, outro)

    def narrate_heal(self, player: Player) -> str:
        intro = self._get_intro(player)
        verb = self._get_verb(BrawlerAction.HEAL, NarrationFallback.DEFAULT)
        outro = self._get_outro(BrawlerAction.HEAL, NarrationFallback.DEFAULT)
        return self._assemble(intro, player.info.name, verb, None, outro)

    def narrate_loot(self, player: Player) -> str:
        intro = self._get_intro(player)
        verb = self._get_verb(BrawlerAction.LOOT, NarrationFallback.DEFAULT)
        outro = self._get_outro(BrawlerAction.LOOT, NarrationFallback.DEFAULT)
        return self._assemble(intro, player.info.name, verb, None, outro)

    def narrate_camp(self, player: Player) -> str:
        intro = self._get_intro(player)
        verb = self._get_verb(BrawlerAction.CAMP, NarrationFallback.DEFAULT)
        outro = self._get_outro(BrawlerAction.CAMP, NarrationFallback.DEFAULT)
        return self._assemble(intro, player.info.name, verb, None, outro)

    def narrate_ambush(self, attacker: Player, target: Player, damage: int) -> str:
        # Ambush logic: force sneaky mood via _get_intro check of last_action
        intro = self._get_intro(attacker)
        verb = self._get_verb(BrawlerAction.AMBUSH, NarrationFallback.DEFAULT)

        if not target.state.alive:
            magnitude = NarrationMagnitude.ELIMINATION
        else:
            magnitude = NarrationFallback.DEFAULT

        outro = self._get_outro(BrawlerAction.AMBUSH, magnitude)
        return self._assemble(intro, attacker.info.name, verb, target.info.name, outro)

    def _assemble(
        self, intro: str, subject: str, verb: str, object: str | None, outro: str
    ) -> str:
        """Assembles the sentence parts with smart capitalization and spacing."""
        if intro:
            sentence = f"{intro} {subject} {verb}"
        else:
            sentence = f"{subject.capitalize()} {verb}"

        if object:
            sentence += f" {object}"

        if outro:
            spacer = "" if outro.startswith(",") or outro.startswith(".") else " "
            sentence += f"{spacer}{outro}"

        return sentence
