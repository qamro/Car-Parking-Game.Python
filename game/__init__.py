# ==============================================================================
# game/__init__.py
# ==============================================================================
# Package initializer for the game logic module.
# Groups all game-related classes and exposes them through a clean interface.
# Demonstrates ENCAPSULATION by controlling module-level visibility.
# ==============================================================================

from game.parking_logic import AbstractParkingSpot, ParkingSpot  # ABSTRACTION + INHERITANCE
from game.obstacle import Obstacle                                # Game obstacle entity
from game.level_manager import LevelManager                       # Level progression
from game.score_manager import ScoreManager                       # Score tracking
from game.camera_controller import CameraController               # Third-person camera

__all__ = [
    "AbstractParkingSpot",
    "ParkingSpot",
    "Obstacle",
    "LevelManager",
    "ScoreManager",
    "CameraController",
]
