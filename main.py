# ruff: noqa: F403, F405

import asyncio

from hunger_game import *
from hunger_game.narration_engine import TextNarrationEngine


def main():
    """Entry point of the simulation."""
    # Load Content
    brawlers = load_json_file(BRAWLER_DATA_FP, parse_brawler_data)
    modes = load_json_file(MODES_DATA_FP, parse_mode_data)
    narration_data = load_json_file(NARRATION_DATA_FP)

    config = MatchConfig()

    # Initialize Narration Engine
    engine = TextNarrationEngine(narration_data, config)

    narrations = Narration(
        match_begin=MatchBeginEventTextNarrator(),
        match_end=MatchEndEventTextNarrator(),
        moment_begin=MomentBeginEventTextNarrator(),
        moment_end=MomentEndEventTextNarrator(),
        attack=AttackEventTextNarrator(engine),
        healing=HealEventTextNarrator(engine),
        loot=LootEventTextNarrator(engine),
        camp=CampEventTextNarrator(engine),
        ambush=AmbushEventTextNarrator(engine),
        poison_gas=PoisonGasEventTextNarrator(),
    )

    # Setup Match
    players = new_players(
        [
            "Alice Johnson",
            "Benjamin Carter",
            "Charlotte Davis",
            "Daniel Martinez",
            "Emma Wilson",
            "Felix Anderson",
            "Grace Thompson",
            "Henry Moore",
            "Isabella Taylor",
            "James Harris",
        ],
        brawlers,
    )

    # Select Mode from Registry
    environment = modes["SOLO_SHOWDOWN"]

    state = MatchState(environment, players, [])

    # Instantiate MatchSimulator
    sim = MatchSimulator(lambda x: MatchNarrator(x, narrations, print), state, config)

    asyncio.run(sim.run())


if __name__ == "__main__":
    main()
