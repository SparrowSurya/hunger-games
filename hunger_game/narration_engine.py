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

    @abc.abstractmethod
    def narrate_poison(self, player: Player, damage: int, context: str) -> T:
        """Narrates poison gas damage."""

    @abc.abstractmethod
    def narrate_eliminations(self, players: list[Player]) -> T:
        """Narrates multiple eliminations at once."""

    @abc.abstractmethod
    def narrate_gas_start(self) -> T:
        """Narrates the event when gas starts covering the map."""

    @abc.abstractmethod
    def narrate_gas_coverage(self) -> T:
        """Narrates the event when gas fully covers the map."""


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

    def narrate_poison(self, player: Player, damage: int, context: str) -> str:
        """Narrates poison damage based on context without numeric values."""
        hp_ratio = player.state.hp / player.info.hitpoints

        if context == "coverage":
            msg = "The map is fully engulfed! "
        elif context == "lazy":
            msg = f"{player.info.name} is caught in the creeping gas! "
        elif context == "cornered":
            msg = f"{player.info.name} is forced into the gas! "
        else:
            msg = f"{player.info.name} chokes on the gas! "

        if not player.state.alive:
            intensity = random.choice(
                [
                    "It's too much—they collapse into the smog.",
                    "The toxic fumes overwhelm them, ending their match.",
                    "They vanish into the green haze, never to return.",
                    "The gas delivers a final, lethal blow.",
                ]
            )
        elif hp_ratio < 0.2:
            intensity = "They are barely clinging to life!"
        elif hp_ratio < 0.5:
            intensity = "They are severely weakened."
        else:
            intensity = "They struggle to breathe but push on."

        return f">> {msg}{intensity}"

    def narrate_eliminations(self, players: list[Player]) -> str:
        """Narrates eliminations using templates from data."""
        names = [p.info.name for p in players]
        count = len(names)

        if count == 1:
            category = "SINGLE"
        elif count == 2:
            category = "DOUBLE"
        else:
            category = "TRIPLE_PLUS"

        templates = self.data.get("eliminations", {}).get(category, ["{0} eliminated."])
        template = random.choice(templates)

        if count == 1:
            return template.format(names[0])
        elif count == 2:
            return template.format(names[0], names[1])
        else:
            # For 3+, the template expects names formatted as a list
            # We'll format the first few and the last one to fit "{0}, and {1}"
            others = ", ".join(names[:-1])
            return template.format(others, names[-1])

    def narrate_gas_coverage(self) -> str:
        """Narrates gas coverage using templates from data."""
        templates = self.data.get("gas_coverage", ["THE GAS HAS COVERED THE MAP!"])
        return random.choice(templates)

    def _assemble(
        self, intro: str, subject: str, verb: str, object: str | None, outro: str
    ) -> str:
        """Assembles the sentence parts with smart capitalization and spacing."""
        if intro:
            sentence = f"{intro} {subject} {verb}"
        else:
            sentence = f"{subject.capitalize()} {verb}"

        if object:
            if "{target}" in verb:
                # Support mid-verb object placement (e.g., "catches {target} off-guard")
                sentence = sentence.replace("{target}", object)
            else:
                sentence += f" {object}"

        if outro:
            spacer = "" if outro.startswith(",") or outro.startswith(".") else " "
            sentence += f"{spacer}{outro}"

        return sentence

    def narrate_gas_start(self) -> str:
        """Narrates the start of poison gas using templates from data."""
        templates = self.data.get("gas_start", ["POISON GAS IS ENTERING THE ARENA!"])
        return random.choice(templates)