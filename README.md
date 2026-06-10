# Hunger Games Simulation

A zero-player simulation engine inspired by Battle Royale mechanics, where AI-controlled Brawlers battle in a narratively driven match. The project focuses on a decoupled architecture where the game simulation and event narration are handled independently through an observer-based system.

## Project Overview

The Hunger Games project simulates a high-stakes match among various Brawlers. Each Brawler is defined by its unique nature (e.g., Tank, Sniper, Artillery) and attack mechanism (e.g., Spread, Projectile, Throwable). Players aren't just names; they are AI entities with specific behavioral traits that influence their decision-making process during the match.

### Key Features

-   **Brawl Stars Themed Narration**: The engine uses a dynamic narration system that captures the atmosphere of Brawl Stars, with specific attack and ambush lines for all 21 brawlers, terminology like "Showdown", "Super", and "Poison Clouds", and a strictly descriptive approach to damage.
-   **Observer-Based Architecture**: The core simulation logic is completely decoupled from the output. A `MatchObserver` monitors the simulator, allowing different types of narrators (text-based, data logs, etc.) to be plugged in seamlessly.
-   **Data-Driven Brawlers**: All Brawler statistics, action weights, and mechanism definitions are loaded from external configuration files, making it easy to balance and expand the roster.
-   **Dynamic AI Weighting**: Players don't act randomly. Their actions are driven by a weighted decision engine that adapts based on their individual traits (Aggressive, Cautious) and the current phase of the match.
-   **Integrated Poison Gas**: Environmental pacing is handled through an integrated poison gas system. Brawlers who are hiding ("lazy") or trapped in combat ("cornered") are contextually damaged as the match progresses, eventually escalating to full map coverage and exponential damage to force a climax.
-   **Strictly Typed Engine**: Built with modern Python features, including generics and deferred type evaluation, ensured by static analysis tools like Pyright.

## Getting Started

This project uses `uv` for dependency management and project execution.

### Prerequisites

-   Python 3.14 or higher
-   [uv](https://github.com/astral-sh/uv) installed on your system

### Installation

Clone the repository and sync the dependencies:

```bash
uv sync
```

### Running the Simulation

To start a new match simulation:

```bash
uv run start
```

### Development Tools

The project includes built-in scripts for maintaining code quality:

-   **Linting (Ruff)**:
    ```bash
    uv run scripts/lint.py
    ```
-   **Type Checking (Pyright)**:
    ```bash
    uv run scripts/type_check.py
    ```

## Architecture

-   **`hunger_game/simulator.py`**: The "brain" of the project. It handles match moments, player turns, and environment dynamics.
-   **`hunger_game/narrator.py`**: Defines the narration system and the `Narration` dataclass which ensures type-safe event reporting.
-   **`hunger_game/match.py`**: Contains the state models and configurations that drive match pacing and rules.
-   **`hunger_game/player.py`**: Manages player entities and their behavioral trait definitions.
-   **`data/`**: Directory containing the JSON definitions for brawlers and match configurations.
