"""
This module provide text based match event narrator classes:
* `TextNarrator`
* `MatchBeginEventTextNarrator`
* `MatchEndEventTextNarrator`
* `MomentBeginEventTextNarrator`
* `MomentEndEventTextNarrator`
* `AttackEventTextNarrator`
* `HealEventTextNarrator`
* `LootEventTextNarrator`
* `CampEventTextNarrator`
* `AmbushEventTextNarrator`
* `PoisonGasEventTextNarrator`
"""

from typing import List, Tuple, override

from hunger_game.match import MatchState
from hunger_game.narrator import EventNarrator
from hunger_game.player import Player
from hunger_game.narration_engine import NarrationEngine


__all__ = (
    "TextNarrator",
    "MatchBeginEventTextNarrator",
    "MatchEndEventTextNarrator",
    "MomentBeginEventTextNarrator",
    "MomentEndEventTextNarrator",
    "AttackEventTextNarrator",
    "HealEventTextNarrator",
    "LootEventTextNarrator",
    "CampEventTextNarrator",
    "AmbushEventTextNarrator",
    "PoisonGasEventTextNarrator",
)


class TextNarrator(EventNarrator[str]):
    """Text based event narrator."""


class MatchBeginEventTextNarrator(TextNarrator):
    """Narrates match start event."""

    @override
    def narrate(self, state: MatchState) -> str:
        border = "=" * 80
        heading = "SOLO SHOWDOWN"
        participants = "\n".join(
            (f"{p.info.name} ({p.name.capitalize()})" for p in state.players)
        )

        return "\n".join(
            [
                border,
                f"{heading:^80}",
                border,
                "",
                "Participants:",
                participants,
            ]
        )


class MatchEndEventTextNarrator(TextNarrator):
    """Narrates match end event."""

    @override
    def narrate(self, state: MatchState, winner: Player | None) -> str:
        border = "=" * 80
        heading = "MATCH ENDED"

        ranked_players = [x[1] for x in state.eliminations]
        if winner is not None:
            ranked_players.append(winner)

        ranks = "\n".join(
            (
                f"#{i:<2} {player.info.name}"
                for i, player in enumerate(reversed(ranked_players), start=1)
            )
        )

        return "\n".join(
            [
                border,
                f"{heading:^80}",
                border,
                "",
                ranks,
            ]
        )


class MomentBeginEventTextNarrator(TextNarrator):
    """Narrates the beginning of a moment."""

    @override
    def narrate(self, moment: int) -> str:
        return f"\n--- MOMENT {moment} ---"


class MomentEndEventTextNarrator(TextNarrator):
    """Narrates the end of a moment."""

    @override
    def narrate(self, alive_count: int) -> str:
        return f"\n[Status: {alive_count} players remain alive]"


class AttackEventTextNarrator(TextNarrator):
    """Narrates an attack using the narration engine."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, attacker: Player, target: Player, damage: int) -> str:
        return self.engine.narrate_attack(attacker, target, damage)


class HealEventTextNarrator(TextNarrator):
    """Narrates a healing event using the narration engine."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, healed: Player, healer: Player | None) -> str:
        return self.engine.narrate_heal(healed)


class LootEventTextNarrator(TextNarrator):
    """Narrates a looting event using the narration engine."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, player: Player) -> str:
        return self.engine.narrate_loot(player)


class CampEventTextNarrator(TextNarrator):
    """Narrates a camping event using the narration engine."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, player: Player) -> str:
        return self.engine.narrate_camp(player)


class AmbushEventTextNarrator(TextNarrator):
    """Narrates an ambush event using the narration engine."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, attacker: Player, target: Player, damage: int) -> str:
        return self.engine.narrate_ambush(attacker, target, damage)


class PoisonGasEventTextNarrator(TextNarrator):
    """Narrates poison gas closing in."""

    @override
    def narrate(self, damaged: List[Tuple[Player, int]]) -> str:
        lines = ["\nTHE POISON GAS IS CLOSING IN!"]
        for player, damage in damaged:
            line = f"  - {player.info.name} takes {damage} damage."
            if not player.state.alive:
                line += " [Eliminated]"
            lines.append(line)
        return "\n".join(lines)
