"""
This module provide text based match event narrator classes:
* `TextNarrator`
* `MatchBeginEventTextNarrator`
* `MatchEndEventTextNarrator`
* `MomentBeginEventTextNarrator`
* `AttackEventTextNarrator`
* `BushCampEventTextNarrator`
* `HealEventTextNarrator`
* `TeamUpEventTextNarrator`
* `CollectEventTextNarrator`
* `StayHiddenEventTextNarrator`
* `BetrayEventTextNarrator`
* `PoisonGasEventTextNarrator`
"""


from typing import List, Tuple, override

from hunger_game.match import MatchState
from hunger_game.narrator import EventNarrator
from hunger_game.player import Player
from hunger_game.game_mode import Collectable


__all__ = (
    "TextNarrator",
    "MatchBeginEventTextNarrator",
    "MatchEndEventTextNarrator",
    "MomentBeginEventTextNarrator",
    "AttackEventTextNarrator",
    "BushCampEventTextNarrator",
    "HealEventTextNarrator",
    "TeamUpEventTextNarrator",
    "CollectEventTextNarrator",
    "StayHiddenEventTextNarrator",
    "BetrayEventTextNarrator",
    "PoisonGasEventTextNarrator",
)


class TextNarrator(EventNarrator[str]):
    """Text based event narrator."""

class MatchBeginEventTextNarrator(TextNarrator):
    """Narrates match start event."""

    @override
    def narrate(self, state: MatchState) -> str: # type: ignore
        border = "=" * 80
        heading = f"🌵 {state.environment.mode.name.upper().replace('_', ' ')} 🌵"
        participants = "\n".join((
            f"{p.name.capitalize()} as {p.info.brawler!s}"
            for p in state.players
        ))

        return "\n".join([
            border,
            f"{heading:^80}",
            border,
            "",
            "Participants:",
            participants,
        ])


class MatchEndEventTextNarrator(TextNarrator):
    """Narrates match end event."""

    @override
    def narrate(self, state: MatchState, winner: Player | None) -> str: # type: ignore
        border = "=" * 80
        heading = "🏆 MATCH ENDED 🏆"
        players = reversed((
            *(x[1] for x in state.eliminations),
            (winner if winner is not None else state.eliminations[-1][0])
        ))
        ranks = "\n".join((
            f"#{i:<2} {player.name.capitalize()}"
            for i, player in enumerate(players, start=1)
        ))

        return "\n".join([
            border,
            f"{heading:^80}",
            border,
            "",
            ranks,
        ])


class MomentBeginEventTextNarrator(TextNarrator):
    """Narrates the beginning of a moment."""

    @override
    def narrate(self, moment: int) -> str: # type: ignore
        return f"\n--- MOMENT {moment} ---"


class AttackEventTextNarrator(TextNarrator):
    """Narrates an attack."""

    @override
    def narrate(self, attacker: Player, target: Player, damage: int, collect: Tuple[Collectable, int] | None) -> str: # type: ignore
        msg = f"• {attacker.name} ({attacker.info.brawler!s}) attacks {target.name} ({target.info.brawler!s}) for {damage} damage."
        if not target.state.alive:
            msg += f" 💀 {target.name} eliminated!"
        if collect:
            msg += f" Collected {collect[1]} {collect[0].name.lower()}s."
        return msg


class BushCampEventTextNarrator(TextNarrator):
    """Narrates a player bush camping."""

    @override
    def narrate(self, camper: Player) -> str: # type: ignore
        return f"• {camper.name} slips into a bush."


class HealEventTextNarrator(TextNarrator):
    """Narrates a healing event."""

    @override
    def narrate(self, healed: Player, healer: Player | None) -> str: # type: ignore
        if healer:
            return f"• {healer.name} heals {healed.name}."
        return f"• {healed.name} regenerates some health."


class TeamUpEventTextNarrator(TextNarrator):
    """Narrates a teamup event."""

    @override
    def narrate(self, source: Player, target: Player, teamed: bool) -> str: # type: ignore
        if teamed:
            return f"• {source.name} spins at {target.name}, and they form an alliance!"
        return f"• {source.name} spins at {target.name}, but they are ignored."


class CollectEventTextNarrator(TextNarrator):
    """Narrates a collection event."""

    @override
    def narrate(self, collector: Player, item: Collectable) -> str: # type: ignore
        return f"• {collector.name} collects a {item.name.lower()}."


class StayHiddenEventTextNarrator(TextNarrator):
    """Narrates a player staying hidden."""

    @override
    def narrate(self, hider: Player) -> str: # type: ignore
        return f"• {hider.name} remains hidden in the shadows."


class BetrayEventTextNarrator(TextNarrator):
    """Narrates a betrayal."""

    @override
    def narrate(self, betrayer: Player, betrayed: Player, damage: int) -> str: # type: ignore
        msg = f"• BETRAYAL! {betrayer.name} turns on {betrayed.name} for {damage} damage!"
        if not betrayed.state.alive:
            msg += f" 💀 {betrayed.name} eliminated!"
        return msg


class PoisonGasEventTextNarrator(TextNarrator):
    """Narrates poison gas closing in."""

    @override
    def narrate(self, damaged: List[Tuple[Player, int]]) -> str: # type: ignore
        lines = ["\n💨 THE POISON GAS IS CLOSING IN!"]
        for player, damage in damaged:
            line = f"  - {player.name} takes {damage} damage."
            if not player.state.alive:
                line += " 💀 Eliminated!"
            lines.append(line)
        return "\n".join(lines)
