# ruff: noqa: F403, F405

import asyncio
from typing import List, Dict, Any

from hunger_game import *


BRAWLERS_DATA: List[Dict[str, Any]] = [
    {
        "brawler": "SHELLY",
        "nature": "DAMAGE_DEALER",
        "actions": {
            "NOTHING": 10, "ATTACK": 60, "BUSH_CAMP": 70, "HEAL": 40,
            "TEAM_UP": 20, "COLLECT": 50, "STAY_HIDDEN": 60, "BETRAY": 40,
        },
        "damage": 45,
        "hitpoionts": 140,
    },
    {
        "brawler": "NITA",
        "nature": "DAMAGE_DEALER",
        "actions": {
            "NOTHING": 15, "ATTACK": 55, "BUSH_CAMP": 30, "HEAL": 50,
            "TEAM_UP": 30, "COLLECT": 60, "STAY_HIDDEN": 20, "BETRAY": 20,
        },
        "damage": 35,
        "hitpoionts": 130,
    },
    {
        "brawler": "COLT",
        "nature": "SNIPER",
        "actions": {
            "NOTHING": 5, "ATTACK": 80, "BUSH_CAMP": 10, "HEAL": 30,
            "TEAM_UP": 10, "COLLECT": 50, "STAY_HIDDEN": 10, "BETRAY": 30,
        },
        "damage": 42,
        "hitpoionts": 90,
    },
    {
        "brawler": "BULL",
        "nature": "TANK",
        "actions": {
            "NOTHING": 10, "ATTACK": 50, "BUSH_CAMP": 90, "HEAL": 40,
            "TEAM_UP": 10, "COLLECT": 40, "STAY_HIDDEN": 80, "BETRAY": 50,
        },
        "damage": 55,
        "hitpoionts": 200,
    },
    {
        "brawler": "JESSIE",
        "nature": "CONTROLLER",
        "actions": {
            "NOTHING": 15, "ATTACK": 50, "BUSH_CAMP": 20, "HEAL": 40,
            "TEAM_UP": 40, "COLLECT": 70, "STAY_HIDDEN": 10, "BETRAY": 10,
        },
        "damage": 32,
        "hitpoionts": 100,
    },
    {
        "brawler": "BROCK",
        "nature": "SNIPER",
        "actions": {
            "NOTHING": 10, "ATTACK": 75, "BUSH_CAMP": 15, "HEAL": 30,
            "TEAM_UP": 10, "COLLECT": 50, "STAY_HIDDEN": 15, "BETRAY": 20,
        },
        "damage": 40,
        "hitpoionts": 80,
    },
    {
        "brawler": "DYNAMIKE",
        "nature": "ARTILLERY",
        "actions": {
            "NOTHING": 10, "ATTACK": 70, "BUSH_CAMP": 20, "HEAL": 30,
            "TEAM_UP": 60, "COLLECT": 40, "STAY_HIDDEN": 40, "BETRAY": 50,
        },
        "damage": 45,
        "hitpoionts": 80,
    },
    {
        "brawler": "TICK",
        "nature": "ARTILLERY",
        "actions": {
            "NOTHING": 20, "ATTACK": 80, "BUSH_CAMP": 40, "HEAL": 20,
            "TEAM_UP": 50, "COLLECT": 30, "STAY_HIDDEN": 50, "BETRAY": 10,
        },
        "damage": 35,
        "hitpoionts": 70,
    },
    {
        "brawler": "EMZ",
        "nature": "CONTROLLER",
        "actions": {
            "NOTHING": 10, "ATTACK": 65, "BUSH_CAMP": 20, "HEAL": 40,
            "TEAM_UP": 20, "COLLECT": 60, "STAY_HIDDEN": 10, "BETRAY": 20,
        },
        "damage": 38,
        "hitpoionts": 110,
    },
    {
        "brawler": "BO",
        "nature": "CONTROLLER",
        "actions": {
            "NOTHING": 15, "ATTACK": 60, "BUSH_CAMP": 50, "HEAL": 40,
            "TEAM_UP": 30, "COLLECT": 50, "STAY_HIDDEN": 40, "BETRAY": 20,
        },
        "damage": 40,
        "hitpoionts": 120,
    },
    {
        "brawler": "EIGHT_BIT",
        "nature": "DAMAGE_DEALER",
        "actions": {
            "NOTHING": 5, "ATTACK": 70, "BUSH_CAMP": 10, "HEAL": 30,
            "TEAM_UP": 10, "COLLECT": 80, "STAY_HIDDEN": 5, "BETRAY": 10,
        },
        "damage": 50,
        "hitpoionts": 150,
    },
]

brawlers = load_brawlers(BRAWLERS_DATA)


players: List[Player] = [
    Player("1", "Amit", brawlers[Brawler.SHELLY], BrawlerState()),
    Player("2", "Deepak", brawlers[Brawler.NITA], BrawlerState()),
    Player("3", "Rahul", brawlers[Brawler.COLT], BrawlerState()),
    Player("4", "Sandeep", brawlers[Brawler.BULL], BrawlerState()),
    Player("5", "Vijay", brawlers[Brawler.JESSIE], BrawlerState()),
    Player("6", "Anil", brawlers[Brawler.BROCK], BrawlerState()),
    Player("7", "Sunil", brawlers[Brawler.DYNAMIKE], BrawlerState()),
    Player("8", "Vikram", brawlers[Brawler.TICK], BrawlerState()),
    Player("9", "Sanjay", brawlers[Brawler.EMZ], BrawlerState()),
    Player("10", "Prakash", brawlers[Brawler.BO], BrawlerState()),
]


text_narrators: Dict[MatchEvent, TextNarrator] = {
    MatchEvent.MATCH_BEGIN: MatchBeginEventTextNarrator(),
    MatchEvent.MATCH_END: MatchEndEventTextNarrator(),
    MatchEvent.MOMENT_BEGIN: MomentBeginEventTextNarrator(),
    MatchEvent.ATTACK: AttackEventTextNarrator(),
    MatchEvent.BUSH_CAMP: BushCampEventTextNarrator(),
    MatchEvent.HEALING: HealEventTextNarrator(),
    MatchEvent.TEAMUP: TeamUpEventTextNarrator(),
    MatchEvent.COLLECT: CollectEventTextNarrator(),
    MatchEvent.HIDING: StayHiddenEventTextNarrator(),
    MatchEvent.BETRAY: BetrayEventTextNarrator(),
    MatchEvent.POSION_GAS: PoisonGasEventTextNarrator(),
}


def main():
    """Entry point of the simulation."""
    global players

    environment = GameModeEnv(
        GameMode.SOLO_SHOWDOWN,
        GameModeConfig(10, GameModeObjective.LAST_PLAYER_STANDING),
        [GameModeDynamic.POISON_GAS],
    )
    state = MatchState(environment, players, [])
    sim = MatchSimulator(lambda x: MatchNarrator(x, text_narrators, print), state) # type: ignore
    asyncio.run(sim.run())


if __name__ == "__main__":
    main()
