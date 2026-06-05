"""
This module provide text based match event narrator classes:
* `TextNarrator`
* `MatchBeginEventTextNarrator`
* `MatchEndEventTextNarrator`
* `MomentBeginEventTextNarrator`
* `MomentEndEventTextNarrator`
* `AttackEventTextNarrator`
* `HealEventTextNarrator`
* `PoisonGasEventTextNarrator`
"""

from typing import List, Tuple, override

from hunger_game.match import MatchState
from hunger_game.narrator import EventNarrator
from hunger_game.player import Player


__all__ = (
    "TextNarrator",
    "MatchBeginEventTextNarrator",
    "MatchEndEventTextNarrator",
    "MomentBeginEventTextNarrator",
    "MomentEndEventTextNarrator",
    "AttackEventTextNarrator",
    "HealEventTextNarrator",
    "PoisonGasEventTextNarrator",
)


class TextNarrator(EventNarrator[str]):
    """Text based event narrator."""


class MatchBeginEventTextNarrator(TextNarrator):
    """Narrates match start event."""

    @override
    def narrate(self, state: MatchState) -> str:
        border = "=" * 80
        heading = f"🌵 {state.environment.mode.name.upper().replace('_', ' ')} 🌵"
        participants = "\n".join(
            (f"{p.name.capitalize()} as {p.info.brawler!s}" for p in state.players)
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
        heading = "🏆 MATCH ENDED 🏆"

        ranked_players = [x[1] for x in state.eliminations]
        if winner is not None:
            ranked_players.append(winner)

        ranks = "\n".join(
            (
                f"#{i:<2} {player.name.capitalize()}"
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
    """Narrates an attack."""

    @override
    def narrate(self, attacker: Player, target: Player, damage: int) -> str:
        msg = f"• {attacker.name} ({attacker.info.brawler!s}) attacks {target.name} ({target.info.brawler!s}) for {damage} damage."
        if not target.state.alive:
            msg += f" 💀 {target.name} eliminated!"
        return msg


class HealEventTextNarrator(TextNarrator):
    """Narrates a healing event."""

    @override
    def narrate(self, healed: Player, healer: Player | None) -> str:
        if healer:
            return f"• {healer.name} heals {healed.name}."
        return f"• {healed.name} regenerates some health."


class PoisonGasEventTextNarrator(TextNarrator):
    """Narrates poison gas closing in."""

    @override
    def narrate(self, damaged: List[Tuple[Player, int]]) -> str:
        lines = ["\n💨 THE POISON GAS IS CLOSING IN!"]
        for player, damage in damaged:
            line = f"  - {player.name} takes {damage} damage."
            if not player.state.alive:
                line += " 💀 Eliminated!"
            lines.append(line)
        return "\n".join(lines)
