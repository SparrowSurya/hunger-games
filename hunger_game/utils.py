"""
This modules provides helper utility functions.
"""

from typing import Dict, List, Any

from hunger_game.brawler import Brawler, BrawlerInfo, BrawlerAction, BrawlerNature


__all__ = (
    "load_brawlers",
)


def load_brawlers(data: List[Dict[str, Any]]) -> Dict[Brawler, BrawlerInfo]:
    """Loads brawlers from raw data."""
    brawlers: Dict[Brawler, BrawlerInfo] = {}
    for item in data:
        raw_actions = item["actions"]
        total = sum(raw_actions.values())
        normalized_actions = {
            BrawlerAction[k]: v / total if total > 0 else 0.0
            for k, v in raw_actions.items()
        }

        brawler_key = Brawler[item["brawler"]]
        brawlers[brawler_key] = BrawlerInfo(
            brawler=brawler_key,
            nature=BrawlerNature[item["nature"]],
            actions=normalized_actions,
            damage=item["damage"],
            hitpoionts=item["hitpoionts"],
        )
    return brawlers
