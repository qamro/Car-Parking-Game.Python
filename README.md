# 3D Car Parking Game

A complete 3D car parking game built in Python using the **Ursina Engine** (built on Panda3D). Features full OOP design with detailed comments explaining every principle.

## Features

- **Third-person 3D camera** with smooth chase behaviour
- **Multiple vehicle types** — Car and Truck with distinct physics (polymorphism)
- **6 progressively challenging levels** — from tutorial to downtown parking
- **Realistic car physics** — acceleration, braking, steering, friction, handbrake
- **Obstacle collision** — barriers, cones, walls, parked cars, pillars, dumpsters
- **Scoring system** — parking accuracy + time bonus + collision penalties + star rating
- **Full menu system** — main menu, pause, level complete, game over screens
- **HUD overlay** — speed, timer, score, collision counter, control hints

## OOP Principles Demonstrated

| Principle | Where |
|---|---|
| **Abstraction** | `AbstractVehicle` (ABC), `AbstractParkingSpot` (ABC) |
| **Encapsulation** | Private attributes + property getters/setters in every class |
| **Inheritance** | `Car` and `Truck` extend `AbstractVehicle`; `ParkingSpot` extends `AbstractParkingSpot` |
| **Polymorphism** | `accelerate()`, `brake()`, `steer()`, `create_model()`, `get_vehicle_type()` — all overridden per vehicle |

## Installation

```bash
pip install ursina
```

## Running

```bash
python main.py
```

## Controls

| Key | Action |
|---|---|
| W / Up Arrow | Accelerate forward |
| S / Down Arrow | Brake / Reverse |
| A / Left Arrow | Steer left |
| D / Right Arrow | Steer right |
| Space | Handbrake |
| R | Restart level |
| V | Switch vehicle (Car ↔ Truck) |
| Escape | Pause / Resume |

## Project Structure

```
car-parking-game/
├── main.py                  # Entry point and game loop
├── requirements.txt         # Dependencies
├── vehicles/
│   ├── abstract_vehicle.py  # Abstract base class (ABC)
│   ├── car.py               # Car implementation
│   └── truck.py             # Truck implementation
├── game/
│   ├── parking_logic.py     # Parking spot detection & scoring
│   ├── obstacle.py          # Obstacle entities & collision
│   ├── level_manager.py     # Level definitions & progression
│   ├── score_manager.py     # Score, timer, star rating
│   └── camera_controller.py # Third-person chase camera
└── ui/
    ├── hud.py               # Heads-up display
    └── menu.py              # Menu screens
```

## Levels

1. **Easy Start** — Straight park, no obstacles
2. **Cone Alley** — Navigate around traffic cones
3. **Parallel Park** — Park between two cars
4. **Parking Garage** — Two spots with pillars and cones
5. **Tight Squeeze** — Narrow gap with barriers
6. **Downtown Lot** — Multiple spots, many obstacles
