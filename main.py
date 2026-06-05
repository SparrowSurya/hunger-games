# ruff: noqa: F403, F405

import asyncio

from hunger_game import *


def main():
    """Entry point of the simulation."""
    narrations = Narration(
        match_begin=MatchBeginEventTextNarrator(),
        match_end=MatchEndEventTextNarrator(),
        moment_begin=MomentBeginEventTextNarrator(),
        moment_end=MomentEndEventTextNarrator(),
        attack=AttackEventTextNarrator(),
        healing=HealEventTextNarrator(),
        poison_gas=PoisonGasEventTextNarrator(),
    )

    brawlers = load_json_file(BRAWLER_DATA_FP, parse_brawler_data)
    players = new_players([
        "Alice Johnson",
        "Benjamin Carter",
        "Charlotte Davis",
        "Daniel Martinez",
        "Emma Wilson",
        "Felix Anderson",
        "Grace Thompson",
        "Henry Moore",
        "Isabella Taylor",
        "James Harris"
    ], brawlers)

    environment = GameModeEnv(
        GameMode.SOLO_SHOWDOWN,
        GameModeConfig(10, GameModeObjective.LAST_PLAYER_STANDING),
        [GameModeDynamic.POISON_GAS],
    )
    state = MatchState(environment, players, [])
    config = MatchConfig()
    sim = MatchSimulator(lambda x: MatchNarrator(x, narrations, print), state, config)
    asyncio.run(sim.run())


if __name__ == "__main__":
    main()
