"""
This modules provides narration engine:
* `NarrationEngine`
* `TextNarrationEngine`
"""

from __future__ import annotations

import abc
import random
from enum import StrEnum, auto
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
    """Internal keys for navigation and access in the narration data structure."""

    INTROS = auto()
    """Key for the introductory phrase templates."""

    VERBS = auto()
    """Key for the action-specific verb templates."""

    OUTROS = auto()
    """Key for the concluding result templates."""


class NarrationMood(StrEnum):
    """Moods used to select brawler-specific intros based on state or traits."""

    AGGRESSIVE = auto()
    """For aggressive brawlers or high-pressure situations."""

    CAUTIOUS = auto()
    """For defensive play or methodical movement."""

    DESPERATE = auto()
    """For brawlers with critically low health."""

    NEUTRAL = auto()
    """The default mood for standard actions."""

    SNEAKY = auto()
    """For actions involving stealth or concealment."""


class NarrationMagnitude(StrEnum):
    """Describes the magnitude of an action's result for outro selection."""

    MINOR = auto()
    """Grazing hits or low-impact results."""

    MAJOR = auto()
    """Devastating strikes or high-impact results."""

    ELIMINATION = auto()
    """Results that conclude a brawler's participation."""


class NarrationFallback(StrEnum):
    """Standard fallback keys for narration data lookups when specific keys aren't found."""

    DEFAULT = auto()
    """The generic template used when no nature or name-specific entry exists."""

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
    def narrate_teamup(
        self, initiator: Player, target: Player, outcome: str, damage: int
    ) -> T:
        """Narrates a teamup attempt."""

    @abc.abstractmethod
    def narrate_betrayal(self, betrayer: Player, victim: Player, damage: int) -> T:
        """Narrates a betrayal."""

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

    def _get_verb(self, action_key: str, player: Player) -> str:
        """Picks a random verb based on action key, brawler name, and nature with 50-50 mix."""
        action_verbs = self.data[NarrationComponent.VERBS].get(action_key, {})

        default_pool = action_verbs.get(NarrationFallback.DEFAULT.name, ["acts"])
        nature_pool = action_verbs.get(player.info.nature.name, [])
        specific_pool = action_verbs.get(player.info.name, [])

        pools = []
        weights = []

        if specific_pool:
            pools.append(specific_pool)
            weights.append(50.0)

            if nature_pool:
                pools.append(nature_pool)
                weights.append(25.0)
                pools.append(default_pool)
                weights.append(25.0)
            else:
                pools.append(default_pool)
                weights.append(50.0)
        else:
            if nature_pool:
                pools.append(nature_pool)
                weights.append(50.0)
                pools.append(default_pool)
                weights.append(50.0)
            else:
                pools.append(default_pool)
                weights.append(100.0)

        chosen_pool = random.choices(pools, weights=weights, k=1)[0]
        return random.choice(chosen_pool)

    def _get_outro(
        self, action_name: str, magnitude: NarrationMagnitude | NarrationFallback
    ) -> str:
        """Picks a random outro based on action and result magnitude."""
        action_outros = self.data[NarrationComponent.OUTROS].get(action_name, {})
        # Note: magnitude might be NarrationMagnitude or NarrationFallback, both are enums.
        # We use .name to match uppercase JSON keys.
        lookup_key = magnitude.name
        outro_pool = action_outros.get(
            lookup_key, action_outros.get(NarrationFallback.DEFAULT.name, [""])
        )
        return random.choice(outro_pool)

    def _get_intro(self, player: Player, action: BrawlerAction | None = None) -> str:
        """Randomly picks an intro based on configuration frequency."""
        # Sneaky mood triggers if currently ambushing OR if they camped last turn
        is_sneaky = (
            action == BrawlerAction.AMBUSH
            or player.state.last_action == BrawlerAction.CAMP
        )

        if is_sneaky:
            mood = NarrationMood.SNEAKY
        elif random.random() > self.config.intro_frequency:
            return ""
        else:
            mood = self._get_mood(player)

        intro_pool = self.data[NarrationComponent.INTROS].get(
            mood.name, self.data[NarrationComponent.INTROS][NarrationMood.NEUTRAL.name]
        )
        return random.choice(intro_pool)

    def narrate_attack(self, attacker: Player, target: Player, damage: int) -> str:
        intro = self._get_intro(attacker, BrawlerAction.ATTACK)

        # Decide voice: 80% Active, 20% Passive
        struct_type = random.choices(["ACTIVE", "PASSIVE"], weights=[80, 20], k=1)[0]
        action_key = "ATTACK" if struct_type == "ACTIVE" else "PASSIVE_ATTACK"
        verb = self._get_verb(action_key, attacker)

        if not target.state.alive:
            magnitude = NarrationMagnitude.ELIMINATION
        elif damage > (target.state.current_max_hp * 0.3):
            magnitude = NarrationMagnitude.MAJOR
        else:
            magnitude = NarrationMagnitude.MINOR

        outro = self._get_outro(BrawlerAction.ATTACK.name, magnitude)
        return self._assemble(struct_type, intro, attacker.info.name, verb, target.info.name, outro)

    def narrate_heal(self, player: Player) -> str:
        intro = self._get_intro(player, BrawlerAction.HEAL)
        verb = self._get_verb(BrawlerAction.HEAL.name, player)
        outro = self._get_outro(BrawlerAction.HEAL.name, NarrationFallback.DEFAULT)
        return self._assemble("ACTIVE", intro, player.info.name, verb, None, outro)

    def narrate_loot(self, player: Player) -> str:
        intro = self._get_intro(player, BrawlerAction.LOOT)
        verb = self._get_verb(BrawlerAction.LOOT.name, player)
        outro = self._get_outro(BrawlerAction.LOOT.name, NarrationFallback.DEFAULT)
        return self._assemble("ACTIVE", intro, player.info.name, verb, None, outro)

    def narrate_camp(self, player: Player) -> str:
        intro = self._get_intro(player, BrawlerAction.CAMP)
        verb = self._get_verb(BrawlerAction.CAMP.name, player)
        outro = self._get_outro(BrawlerAction.CAMP.name, NarrationFallback.DEFAULT)
        return self._assemble("ACTIVE", intro, player.info.name, verb, None, outro)

    def narrate_ambush(self, attacker: Player, target: Player, damage: int) -> str:
        intro = self._get_intro(attacker, BrawlerAction.AMBUSH)

        # Decide voice: 80% Active, 20% Passive
        struct_type = random.choices(["ACTIVE", "PASSIVE"], weights=[80, 20], k=1)[0]
        action_key = "AMBUSH" if struct_type == "ACTIVE" else "PASSIVE_AMBUSH"
        verb = self._get_verb(action_key, attacker)

        if not target.state.alive:
            magnitude = NarrationMagnitude.ELIMINATION
        else:
            magnitude = NarrationFallback.DEFAULT

        outro = self._get_outro(BrawlerAction.AMBUSH.name, magnitude)
        return self._assemble(struct_type, intro, attacker.info.name, verb, target.info.name, outro)

    def narrate_teamup(self, initiator: Player, target: Player, outcome: str, damage: int) -> str:
        """Narrates a teamup attempt and its result."""
        intro = self._get_intro(initiator, BrawlerAction.TEAMUP)
        verb = self._get_verb(BrawlerAction.TEAMUP.name, initiator)

        # Special case: override the lookup to use the outcome name
        action_outros = self.data[NarrationComponent.OUTROS].get(BrawlerAction.TEAMUP.name, {})
        outro_pool = action_outros.get(outcome, [""])
        outro = random.choice(outro_pool)

        return self._assemble("ACTIVE", intro, initiator.info.name, verb, target.info.name, outro)

    def narrate_betrayal(self, betrayer: Player, victim: Player, damage: int) -> str:
        """Narrates a backstab."""
        intro = self._get_intro(betrayer, BrawlerAction.BETRAY)
        verb = self._get_verb(BrawlerAction.BETRAY.name, betrayer)

        if not victim.state.alive:
            magnitude = NarrationMagnitude.ELIMINATION
        else:
            magnitude = NarrationFallback.DEFAULT

        outro = self._get_outro(BrawlerAction.BETRAY.name, magnitude)
        return self._assemble("ACTIVE", intro, betrayer.info.name, verb, victim.info.name, outro)

    def narrate_poison(self, player: Player, damage: int, context: str) -> str:
        """Narrates poison damage based on context without numeric values."""
        hp_ratio = player.state.hp / player.info.hitpoints
        poison_data = self.data.get("poison", {})
        messages = poison_data.get("messages", {})
        intensities = poison_data.get("intensities", {})

        msg_template = messages.get(
            context, messages.get("default", "{0} chokes on the gas! ")
        )
        msg = msg_template.format(player.info.name)

        if not player.state.alive:
            elimination_pool = intensities.get(
                "elimination", ["The gas delivers a final, lethal blow."]
            )
            intensity = random.choice(elimination_pool)
        elif hp_ratio < 0.2:
            intensity = intensities.get("critical", "They are barely clinging to life!")
        elif hp_ratio < 0.5:
            intensity = intensities.get("moderate", "They are severely weakened.")
        else:
            intensity = intensities.get(
                "minor", "They struggle to breathe but push on."
            )

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
        self,
        struct_type: str,
        intro: str,
        subject: str,
        verb: str,
        object: str | None,
        outro: str,
    ) -> str:
        """Assembles the sentence parts using structural templates from data."""
        structures = self.data.get("structures", {})
        templates = structures.get(struct_type, structures.get("ACTIVE", []))
        template = random.choice(templates)

        # Prepare components
        fmt_target = object if object else ""
        fmt_verb = verb

        # If the verb contains {target}, we embed it and clear fmt_target
        if "{target}" in verb:
            fmt_verb = verb.replace("{target}", fmt_target)
            fmt_target = ""

        components = {
            "intro": intro,
            "subject": subject,
            "verb": fmt_verb,
            "target": fmt_target,
        }

        # Populate template
        sentence = template
        for key, val in components.items():
            sentence = sentence.replace(f"{{{key}}}", val)

        # Cleanup spacing and handle capitalization
        sentence = sentence.strip().replace("  ", " ")
        if sentence:
            # If no intro was used, ensure the first character is capitalized
            if not intro or not sentence.startswith(intro):
                sentence = sentence[0].upper() + sentence[1:]

        # Re-apply outro logic (handling spacing and punctuation)
        if outro:
            spacer = "" if outro.startswith(",") or outro.startswith(".") else " "
            sentence += f"{spacer}{outro}"

        # Ensure sentence ends with a period if no punctuation is present
        if not sentence.endswith((".", "!", "?")):
            sentence += "."

        return sentence

    def narrate_gas_start(self) -> str:
        """Narrates the start of poison gas using templates from data."""
        templates = self.data.get("gas_start", ["POISON GAS IS ENTERING THE ARENA!"])
        return random.choice(templates)
