"""
This modules provides game mode related classes:
* `GameModeObjective`
* `GameModeConfig`
* `GameModeDynamic`
* `GameModeEnv`
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum, auto


__all__ = (
    "GameModeObjective",
    "GameModeConfig",
    "GameModeDynamic",
    "GameModeEnv",
)


class GameModeObjective(StrEnum):
    """Defines the primary goal of the match, influencing win conditions."""

    LAST_PLAYER_STANDING = auto()
    """A standard Battle Royale format where only the final survivor wins."""


class GameModeDynamic(StrEnum):
    """Environmental hazards or match-wide modifiers."""

    POISON_GAS = auto()
    """An encroaching hazard that deals damage over time and forces players together."""

@dataclass(repr=False)
class PoisonGasConfig:
    """Configuration for poison gas dynamics."""

    safe_until: int
    """The moment until which the map is completely safe from poison gas."""

    full_coverage_at: int
    """The moment at which the poison gas covers the entire map."""

    base_damage: int
    """The starting damage value for poison gas."""

    scaling_factor: float
    """The percentage increase in gas damage per moment after full coverage."""

    random_hit_chance: float
    """Baseline chance for any player to be grazed by gas during creeping phase."""

    lazy_hit_chance: float
    """Higher chance for CAMPING or ISOLATED players to take gas damage."""

    cornered_hp_threshold: float
    """HP ratio below which a player is considered 'cornered' during combat."""

    cornered_hit_chance: float
    """Chance for a 'cornered' player to take gas damage when attacked."""


@dataclass(repr=False)
class PowerCubeConfig:
    """Configuration for power cube bonuses."""

    damage_multiplier: float
    """Damage boost percentage per power cube collected (e.g., 0.1 for 10%)."""

    hp_bonus_ratio: float
    """Max HP increase ratio per power cube (e.g., 0.25 for 25% of base HP)."""

    instant_heal_ratio: float
    """HP restored immediately upon picking up a cube (e.g., 0.25 for 25% of base HP)."""


@dataclass(repr=False)
class AmbushConfig:
    """Configuration for ambush mechanics."""

    bonus_multiplier: float
    """Damage multiplier applied when attacking from a hidden (CAMP) state."""


@dataclass(repr=False)
class PhaseConfig:
    """Configuration for action weight multipliers during a specific match phase."""

    attack_multiplier: float = 1.0
    """Multiplier applied to ATTACK action weight."""

    loot_multiplier: float = 1.0
    """Multiplier applied to LOOT action weight."""


@dataclass(repr=False)
class MatchPhasesConfig:
    """Action weight adjustments for the three core match phases."""

    early: PhaseConfig
    """Multipliers for the initial phase of the match."""

    mid: PhaseConfig
    """Multipliers for the mid-game (once player count drops)."""

    late: PhaseConfig
    """Multipliers for the endgame showdown."""


@dataclass(repr=False)
class GameModeConfig:
    """Configuration for a game mode, loaded from data."""

    max_players: int
    """Maximum players allowed in this mode."""

    damage_variance: int
    """Random spread added or subtracted from a brawler's base damage."""

    heal_min: int
    """Minimum HP restored during a HEAL action."""

    heal_max: int
    """Maximum HP restored during a HEAL action."""

    mid_game_threshold: float
    """Percentage of players remaining to trigger mid-game aggression levels."""

    end_game_threshold: float
    """Percentage of players remaining to trigger end-game aggression levels."""

    phases: MatchPhasesConfig | None = None
    """Phase-based action weight modifiers."""

    power_cubes: PowerCubeConfig | None = None
    """Power cube configuration if the mode includes it."""

    ambush: AmbushConfig | None = None
    """Ambush configuration if the mode includes it."""

    gas: PoisonGasConfig | None = None
    """Poison gas configuration if the mode includes it."""


@dataclass(repr=False)
class GameModeEnv:
    """Environment for a game mode."""

    name: str
    """Name of the game mode."""

    objective: GameModeObjective
    """Objective ofthe game mode."""

    dynamics: list[GameModeDynamic]
    """Dynamic environment factors in game mode."""

    config: GameModeConfig
    """Game mode configurations."""
