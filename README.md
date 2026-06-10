# Hunger Games Simulation

A zero-player simulation engine inspired by Battle Royale mechanics, where AI-controlled Brawlers battle in a narratively driven match. The project focuses on a decoupled architecture where the game simulation is completely independent of the narration.

## 🚀 Key Features

-   **Brawl Stars Themed Narration**: A dynamic narration system with specific attack, ambush, and betrayal lines for all characters, utilizing terminology like "Showdown" and "Super".
-   **Power Cube Mechanic**: Functional looting system where brawlers gain damage (+10%) and HP (+400) by collecting power cubes during the match.
-   **Multiplicative Trait System**: Brawler behavior is driven by randomized traits (Aggressive, Camper, Ambuser, etc.) that apply significant multipliers to action weights, ensuring distinct character personalities.
-   **Advanced Encounter System**: Simulates spatial dynamics through ISOLATED, DUEL, and MELEE states, managing who can interact with whom without a coordinate grid.
-   **Hardcore Survival Loop**: Environmental poison gas that escalates damage and disables healing for non-support brawlers in the endgame to force a decisive finish.
-   **Observer-Based Architecture**: Core simulation is decoupled from output, allowing for various narrators (text, data logs, etc.) to be plugged in seamlessly.
-   **Strictly Typed Engine**: Built with Python 3.14 features, ensuring 100% type safety via Pyright.

## 🛠️ Tech Stack

-   **Python 3.14+** (using generics and deferred annotations)
-   **uv** (package management)
-   **Ruff** (linting and formatting)
-   **Pyright** (static type checking)

## 📂 Core Structure

-   **`hunger_game/simulator.py`**: Core loop, encounter management, and result calculation.
-   **`hunger_game/narration_engine.py`**: Unified pipeline for transforming events into structured sentences.
-   **`hunger_game/brawler.py`**: Brawler state tracking, including HP, damage multipliers, and power cubes.
-   **`hunger_game/match.py`**: Global configuration and state models.
-   **`hunger_game/events.py`**: Unified match event model definitions.
-   **`hunger_game/game_mode.py`**: Objective and environmental hazard models.
-   **`hunger_game/player.py`**: Player instance models and behavioral trait definitions.
-   **`hunger_game/observer.py`**: Base interface for match monitoring (Observer Pattern).
-   **`hunger_game/text_narrator.py`**: Text-based implementation of event narrators.
-   **`hunger_game/constants.py`**: Engine-wide constants and path configurations.
-   **`hunger_game/utils.py`**: Helpers for JSON loading and weight normalization.
-   **`data/`**: JSON definitions for brawlers, modes, and narration templates.

## 🏃 Running the Simulation

```bash
uv run start
```

## 🧪 Development & Quality

Ensure code quality before committing:

```bash
uv run python scripts/lint.py
uv run python scripts/type_check.py
uv run python scripts/format.py
```
