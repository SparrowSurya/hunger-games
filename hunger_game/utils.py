"""
This modules provides helper utility functions.
"""

import json
import random
from typing import Dict, List, Tuple, Any, Callable, overload

from hunger_game.brawler import BrawlerInfo, BrawlerAction, BrawlerState
from hunger_game.game_mode import (
    GameModeEnv,
    GameModeObjective,
    GameModeDynamic,
    GameModeConfig,
    PoisonGasConfig,
)
from hunger_game.player import Player, PlayerTrait


__all__ = (
    "load_json_file",
    "parse_brawler_data",
    "parse_mode_data",
    "new_players",
    "random_traits",
    "normalise_weights_mut",
    "normalise_weights",
)


@overload
def load_json_file(path: str) -> Any:
    """Loads the json file as raw data."""


@overload
def load_json_file[T](path: str, parser: Callable[[Any], T]) -> T:
    """Loads the json file and provides parsed input."""


def load_json_file[T](path: str, parser: Callable[[Any], T] | None = None) -> T | Any:
    """Loads json file and parses the file if parser is provided."""
    with open(path, "r") as f:
        result = json.load(f)

    if parser:
        return parser(result)
    return result


def parse_brawler_data(data: Dict[str, Any]) -> Dict[str, BrawlerInfo]:
    """Parses brawler info from json data."""
    brawlers: Dict[str, BrawlerInfo] = {}
    for item in data["brawlers"]:
        name = item["brawler"]
        brawlers[name] = BrawlerInfo(
            name=name,
            nature=item["nature"],
            damage=item["damage"],
            hitpoints=item["hitpoints"],
        )
    return brawlers


def parse_mode_data(data: Dict[str, Any]) -> Dict[str, GameModeEnv]:
    """Parses game mode info from json data."""
    modes: Dict[str, GameModeEnv] = {}
    for name, details in data.items():
        config_data = details["config"].copy()
        gas_config = None
        if "gas" in config_data:
            gas_config = PoisonGasConfig(**config_data.pop("gas"))

        modes[name] = GameModeEnv(
            name=name,
            objective=GameModeObjective[details["objective"]],
            dynamics=[GameModeDynamic[d] for d in details["dynamics"]],
            config=GameModeConfig(gas=gas_config, **config_data),
        )
    return modes


def new_players(names: List[str], brawlers: Dict[str, BrawlerInfo]) -> List[Player]:
    """Populates players with random brawlers."""
    brawler_names = list(brawlers.keys())
    random.shuffle(brawler_names)

    return [
        Player(
            str(i),
            name,
            brawlers[brawler_names[i % len(brawler_names)]],
            BrawlerState(action_weights=random_action_weights()),
            random_traits(),
        )
        for i, name in enumerate(names)
    ]


def random_action_weights() -> Dict[BrawlerAction, float]:
    """Provides random action weights with a few high and rest low distribution."""
    actions = list(BrawlerAction)
    random.shuffle(actions)

    # Pick 1 or 2 actions to be high weight
    high_count = random.randint(1, 2)
    weights: Dict[BrawlerAction, float] = {}

    for i, action in enumerate(actions):
        if i < high_count:
            weights[action] = float(random.randint(60, 100))
        else:
            weights[action] = float(random.randint(5, 20))

    return weights


def random_traits() -> List[Tuple[PlayerTrait, float]]:
    """Provides random traits."""
    traits = list(PlayerTrait)
    random.shuffle(traits)

    output: List[Tuple[PlayerTrait, float]] = []

    # Pick between 1 and the max number of traits available
    for i in range(random.randint(1, len(traits))):
        trait = traits[i]
        output.append((trait, random.randint(6, 10)))

    return normalise_weights(output, lambda x: x[1], lambda x, w: (x[0], w))


def normalise_weights_mut[T](
    items: List[T],
    getter: Callable[[T], float],
    setter: Callable[[T, float], None],
):
    """Normalises the weights of mutable item."""
    total = sum(getter(item) for item in items)
    for item in items:
        setter(item, getter(item) / total if total > 0 else 0)


def normalise_weights[T](
    items: List[T],
    getter: Callable[[T], float],
    setter: Callable[[T, float], T],
) -> List[T]:
    """Normalises the weights of immutable item."""
    total = sum(getter(item) for item in items)
    return [setter(item, getter(item) / total if total > 0 else 0) for item in items]
