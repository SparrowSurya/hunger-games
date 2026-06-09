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
* `PoisonGasCoverageEventTextNarrator`
"""

from typing import override
from hunger_game.events import (
    MatchEventModel,
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
    PoisonGasCoverageEvent,
    PoisonGasStartEvent,
)

from hunger_game.narrator import EventNarrator
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
    "PoisonGasStartEventTextNarrator",
    "PoisonGasCoverageEventTextNarrator",
)


class TextNarrator[M: MatchEventModel](EventNarrator[M, str]):
    """Text based event narrator."""


class MatchBeginEventTextNarrator(TextNarrator[MatchBeginEvent]):
    """Narrates match start event."""

    @override
    def narrate(self, event: MatchBeginEvent) -> str:
        border = "=" * 80
        heading = "SOLO SHOWDOWN"
        participants = "\n".join(
            (f"{p.info.name} ({p.name.capitalize()})" for p in event.state.players)
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


class MatchEndEventTextNarrator(TextNarrator[MatchEndEvent]):
    """Narrates match end event."""

    @override
    def narrate(self, event: MatchEndEvent) -> str:
        border = "=" * 80
        heading = "MATCH ENDED"

        ranked_players = [x[1] for x in event.state.eliminations]
        if event.winner is not None:
            ranked_players.append(event.winner)

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


class MomentBeginEventTextNarrator(TextNarrator[MomentBeginEvent]):
    """Narrates the beginning of a moment."""

    @override
    def narrate(self, event: MomentBeginEvent) -> str:
        return f"\n--- MOMENT {event.moment} ---"


class MomentEndEventTextNarrator(TextNarrator[MomentEndEvent]):
    """Narrates the end of a moment with eliminations."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, event: MomentEndEvent) -> str:
        lines: list[str] = []
        if event.eliminated:
            sentence = self.engine.narrate_eliminations(event.eliminated)
            lines.append(f"\n[Eliminations: {sentence}]")

        lines.append(f"\n[Status: {event.alive_count} players remain alive]")
        return "".join(lines)


class AttackEventTextNarrator(TextNarrator[AttackEvent]):
    """Narrates an attack using the narration engine."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, event: AttackEvent) -> str:
        return self.engine.narrate_attack(event.attacker, event.target, event.damage)


class HealEventTextNarrator(TextNarrator[HealEvent]):
    """Narrates a healing event using the narration engine."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, event: HealEvent) -> str:
        return self.engine.narrate_heal(event.healed)


class LootEventTextNarrator(TextNarrator[LootEvent]):
    """Narrates a looting event using the narration engine."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, event: LootEvent) -> str:
        return self.engine.narrate_loot(event.player)


class CampEventTextNarrator(TextNarrator[CampEvent]):
    """Narrates a camping event using the narration engine."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, event: CampEvent) -> str:
        return self.engine.narrate_camp(event.player)


class AmbushEventTextNarrator(TextNarrator[AmbushEvent]):
    """Narrates an ambush event using the narration engine."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, event: AmbushEvent) -> str:
        return self.engine.narrate_ambush(event.attacker, event.target, event.damage)


class PoisonGasEventTextNarrator(TextNarrator[PoisonDamageEvent]):
    """Narrates poison gas damage using the narration engine."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, event: PoisonDamageEvent) -> str:
        return self.engine.narrate_poison(event.player, event.damage, event.context)


class PoisonGasCoverageEventTextNarrator(TextNarrator[PoisonGasCoverageEvent]):
    """Narrates poison gas covering the map using the narration engine."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, event: PoisonGasCoverageEvent) -> str:
        return self.engine.narrate_gas_coverage()

class PoisonGasStartEventTextNarrator(TextNarrator[PoisonGasStartEvent]):
    """Narrates posion gas started on the map using the narration engine."""

    def __init__(self, engine: NarrationEngine[str]):
        self.engine = engine

    @override
    def narrate(self, event: PoisonGasStartEvent) -> str:
        return self.engine.narrate_gas_start()