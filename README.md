# Titi_mario_game (Mario vs Zombies) Game with Reinforcement Learning Data Logging

## Description

This is a simple web-based game where a character (Mario) must avoid zombies. The game dynamically spawns zombies, which move toward Mario, and the player must use arrow keys to avoid collisions. Additionally, this implementation includes functionality to log game state data for reinforcement learning purposes.

The game state, including player movements, zombie spawns, and collisions, is saved as JSON data, which can be used for training a reinforcement learning model. The data is saved with a timestamped filename.

## Features

- **Dynamic Zombie Spawning**: Zombies are spawned at random positions and move toward Mario at increasing speeds.
- **Player Movement**: Control Mario using the arrow keys (`↑`, `↓`, `←`, `→`).
- **Collision Detection**: The game detects collisions between Mario and zombies, ending the game if a collision occurs.
- **Reinforcement Learning Data Logging**: The game logs key events (player movements, zombie spawns, collisions) into a JSON file, which is automatically downloaded when the game ends.

## Data Logging
**The game logs the following data:**

- **Score**: The current score at each event.
- **Mario's Position**: The X and Y coordinates of Mario.
- **Zombie Positions**: The X and Y coordinates of all zombies on the screen.
- **Event Type**: The type of event (e.g., move, spawn, collision).
- **Timestamp**: The exact time each event occurred.

The data is saved in a JSON file with a filename in the format training_data_YYYY-MM-DD_HHhMMSSs.json, where YYYY-MM-DD is the date and HHhMM is the time.

**Example**:
```json
[
  {
    "timestamp": "2024-08-27T23:19:30.123Z",
    "score": 5,
    "marioPosition": {
      "left": 150,
      "top": 200
    },
    "obstacles": [
      {"left": 100, "top": 300},
      {"left": 200, "top": 100}
    ],
    "speed": 5.3,
    "actionType": "move",
    "actionDetail": "right"
  },
  {
    "timestamp": "2024-08-27T23:19:32.456Z",
    "score": 6,
    "marioPosition": {
      "left": 170,
      "top": 200
    },
    "obstacles": [
      {"left": 100, "top": 350},
      {"left": 220, "top": 150}
    ],
    "speed": 5.6,
    "actionType": "collision",
    "actionDetail": "zombie"
  }
]
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/3npC0nf1g/Titi_mario_game.git
cd Titi_mario_game
```
