"""
This modules provides helper utility functions.
"""

import json
import random
from typing import Dict, List, Tuple, Any, Callable, overload

from hunger_game.brawler import Brawler, BrawlerInfo, BrawlerAction, BrawlerNature, BrawlerState, BrawlerAttack
from hunger_game.player import Player, PlayerTrait


__all__ = (
    "load_json_file",
    "parse_brawler_data",
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
    with open(path, 'r') as f:
        result = json.load(f)

    if parser:
        return parser(result)
    return result


def parse_brawler_data(data: List[Dict[str, Any]]) -> Dict[Brawler, BrawlerInfo]:
    """Parses brawler info from json data."""
    brawlers: Dict[Brawler, BrawlerInfo] = {}
    for item in data:
        raw_actions = list(item["actions"].items())
        normalized_actions = {
            BrawlerAction[k]: w
            for k, w in normalise_weights(raw_actions, lambda x: x[1], lambda x, w: (x[0], w))
        }

        brawler_key = Brawler[item["brawler"]]
        brawlers[brawler_key] = BrawlerInfo(
            brawler=brawler_key,
            nature=BrawlerNature[item["nature"]],
            attack=BrawlerAttack[item["attack"]],
            actions=normalized_actions,
            damage=item["damage"],
            hitpoints=item["hitpoints"],
        )
    return brawlers


def new_players(names: List[str], brawlers: Dict[Brawler, BrawlerInfo]) -> List[Player]:
    """Populates players with random brawlers."""
    keys = list(brawlers.keys())
    random.shuffle(keys)

    return [
        Player(str(i), name, brawlers[keys[i]], BrawlerState(), random_traits())
        for i, name in enumerate(names)
    ]

def random_traits() -> List[Tuple[PlayerTrait, float]]:
    """Provides random traits."""
    traits = list(PlayerTrait)
    random.shuffle(traits)

    output: List[Tuple[PlayerTrait, float]] = []

    # Pick between 1 and the max number of traits available
    for i in range(random.randint(1, len(traits))):
        trait = traits[i]
        output.append((trait, random.randint(1, 10)))

    return normalise_weights(output, lambda x: x[1], lambda x, w: (x[0], w))


def normalise_weights_mut[T](
    items: List[T],
    getter: Callable[[T], float],
    setter: Callable[[T, float], None],
):
    """Normalises the weights of mutable item."""
    total = sum(getter(item) for item in items)
    for item in items:
        setter(item, getter(item) / total)

def normalise_weights[T](
    items: List[T],
    getter: Callable[[T], float],
    setter: Callable[[T, float], T],
) -> List[T]:
    """Normalises the weights of immutable item."""
    total = sum(getter(item) for item in items)
    return [setter(item, getter(item) / total) for item in items]
