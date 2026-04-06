# ==============================================================================
# game/level_manager.py
# ==============================================================================
# Manages level definitions, progression, and scene setup / teardown.
#
# ENCAPSULATION: Level data and current-level index are private; the public
# interface exposes only what the game loop needs.
#
# Each level is a dictionary describing spawn position, parking spots, and
# obstacles.  The manager creates / destroys scene objects when levels change.
# ==============================================================================

from ursina import Vec3                           # 3-D vector type
from game.parking_logic import ParkingSpot        # Concrete parking spot
from game.obstacle import Obstacle                # Obstacle entities


class LevelManager:
    """Stores and manages all game levels.

    ENCAPSULATION — level data is private; the game loop interacts through
    load_level(), next_level(), and property accessors only.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(self) -> None:
        # ENCAPSULATION: private level state
        self._current_level_index: int = 0          # Which level is active
        self._levels: list[dict] = []               # Level definition list
        self._active_spots: list[ParkingSpot] = []  # Currently spawned spots
        self._active_obstacles: list[Obstacle] = [] # Currently spawned obstacles

        # Populate the built-in level catalogue
        self._build_levels()

    # ------------------------------------------------------------------
    # Properties (ENCAPSULATION — read-only access to internal state)
    # ------------------------------------------------------------------
    @property
    def current_level_index(self) -> int:
        """Return 0-based index of the current level."""
        return self._current_level_index

    @property
    def current_level_number(self) -> int:
        """Return 1-based level number for display."""
        return self._current_level_index + 1

    @property
    def total_levels(self) -> int:
        """Return the total number of levels."""
        return len(self._levels)

    @property
    def active_spots(self) -> list[ParkingSpot]:
        """Return currently active parking spots."""
        return self._active_spots

    @property
    def active_obstacles(self) -> list[Obstacle]:
        """Return currently active obstacles."""
        return self._active_obstacles

    @property
    def spawn_position(self) -> Vec3:
        """Return the player spawn position for the current level."""
        level = self._levels[self._current_level_index]
        return Vec3(level["spawn_position"])

    @property
    def spawn_rotation(self) -> float:
        """Return the player spawn yaw for the current level."""
        return self._levels[self._current_level_index]["spawn_rotation"]

    @property
    def level_name(self) -> str:
        """Return the display name of the current level."""
        return self._levels[self._current_level_index]["name"]

    @property
    def time_limit(self) -> float:
        """Return the time limit in seconds for the current level."""
        return self._levels[self._current_level_index]["time_limit"]

    # ------------------------------------------------------------------
    # Level catalogue (private)
    # ------------------------------------------------------------------
    def _build_levels(self) -> None:
        """Define all game levels.

        Each level dictionary contains:
        - name: display title
        - spawn_position / spawn_rotation: player start
        - time_limit: seconds to complete
        - spots: list of parking spot specs
        - obstacles: list of obstacle specs
        """
        self._levels = [
            # ==============================================================
            # Level 1 — Tutorial: simple straight park, no obstacles
            # ==============================================================
            {
                "name": "Easy Start",
                "spawn_position": (0, 0, -8),
                "spawn_rotation": 0,
                "time_limit": 60,
                "spots": [
                    {"position": (0, 0, 5), "rotation": 0},
                ],
                "obstacles": [],
            },
            # ==============================================================
            # Level 2 — Side parking with a few cones
            # ==============================================================
            {
                "name": "Cone Alley",
                "spawn_position": (-6, 0, -6),
                "spawn_rotation": 45,
                "time_limit": 75,
                "spots": [
                    {"position": (4, 0, 4), "rotation": 90},
                ],
                "obstacles": [
                    {"position": (1, 0.2, 2), "type": "cone",
                     "scale": (0.3, 0.5, 0.3)},
                    {"position": (6, 0.2, 2), "type": "cone",
                     "scale": (0.3, 0.5, 0.3)},
                    {"position": (4, 0.2, -1), "type": "cone",
                     "scale": (0.3, 0.5, 0.3)},
                ],
            },
            # ==============================================================
            # Level 3 — Parallel park between parked cars
            # ==============================================================
            {
                "name": "Parallel Park",
                "spawn_position": (0, 0, -10),
                "spawn_rotation": 0,
                "time_limit": 90,
                "spots": [
                    {"position": (5, 0, 0), "rotation": 90},
                ],
                "obstacles": [
                    {"position": (5, 0.25, 4), "type": "parked_car",
                     "scale": (1, 0.5, 2.2), "rotation": 90},
                    {"position": (5, 0.25, -4), "type": "parked_car",
                     "scale": (1, 0.5, 2.2), "rotation": 90},
                    {"position": (-3, 0.5, 0), "type": "wall",
                     "scale": (0.3, 1, 12)},
                ],
            },
            # ==============================================================
            # Level 4 — Multi-spot parking garage
            # ==============================================================
            {
                "name": "Parking Garage",
                "spawn_position": (0, 0, -12),
                "spawn_rotation": 0,
                "time_limit": 90,
                "spots": [
                    {"position": (-4, 0, 6), "rotation": 0},
                    {"position": (4, 0, 6), "rotation": 0},
                ],
                "obstacles": [
                    {"position": (0, 0.5, 6), "type": "pillar",
                     "scale": (0.5, 1, 0.5)},
                    {"position": (-7, 0.5, 0), "type": "wall",
                     "scale": (0.3, 1, 18)},
                    {"position": (7, 0.5, 0), "type": "wall",
                     "scale": (0.3, 1, 18)},
                    {"position": (0, 0.2, 0), "type": "cone",
                     "scale": (0.3, 0.5, 0.3)},
                    {"position": (-2, 0.2, 3), "type": "cone",
                     "scale": (0.3, 0.5, 0.3)},
                    {"position": (2, 0.2, 3), "type": "cone",
                     "scale": (0.3, 0.5, 0.3)},
                ],
            },
            # ==============================================================
            # Level 5 — Tight squeeze with barriers
            # ==============================================================
            {
                "name": "Tight Squeeze",
                "spawn_position": (-8, 0, -8),
                "spawn_rotation": 30,
                "time_limit": 100,
                "spots": [
                    {"position": (0, 0, 5), "rotation": 0},
                ],
                "obstacles": [
                    {"position": (-2, 0.3, 5), "type": "barrier",
                     "scale": (0.3, 0.6, 3)},
                    {"position": (2, 0.3, 5), "type": "barrier",
                     "scale": (0.3, 0.6, 3)},
                    {"position": (0, 0.3, 0), "type": "barrier",
                     "scale": (6, 0.6, 0.3)},
                    {"position": (-5, 0.2, -3), "type": "cone",
                     "scale": (0.3, 0.5, 0.3)},
                    {"position": (5, 0.2, -3), "type": "cone",
                     "scale": (0.3, 0.5, 0.3)},
                    {"position": (-5, 0.25, 3), "type": "dumpster",
                     "scale": (1.2, 0.5, 0.8)},
                ],
            },
            # ==============================================================
            # Level 6 — Advanced: multiple spots, many obstacles
            # ==============================================================
            {
                "name": "Downtown Lot",
                "spawn_position": (0, 0, -14),
                "spawn_rotation": 0,
                "time_limit": 120,
                "spots": [
                    {"position": (-5, 0, 8), "rotation": 90},
                    {"position": (5, 0, 8), "rotation": 90},
                ],
                "obstacles": [
                    {"position": (-5, 0.25, 4), "type": "parked_car",
                     "scale": (1, 0.5, 2.2), "rotation": 90},
                    {"position": (5, 0.25, 12), "type": "parked_car",
                     "scale": (1, 0.5, 2.2), "rotation": 90},
                    {"position": (0, 0.5, 8), "type": "pillar",
                     "scale": (0.5, 1, 0.5)},
                    {"position": (-8, 0.5, 0), "type": "wall",
                     "scale": (0.3, 1, 20)},
                    {"position": (8, 0.5, 0), "type": "wall",
                     "scale": (0.3, 1, 20)},
                    {"position": (0, 0.3, -5), "type": "barrier",
                     "scale": (8, 0.6, 0.3)},
                    {"position": (-3, 0.2, -2), "type": "cone",
                     "scale": (0.3, 0.5, 0.3)},
                    {"position": (3, 0.2, -2), "type": "cone",
                     "scale": (0.3, 0.5, 0.3)},
                    {"position": (0, 0.2, 2), "type": "cone",
                     "scale": (0.3, 0.5, 0.3)},
                ],
            },
        ]

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def load_level(self) -> None:
        """Instantiate parking spots and obstacles for the current level.

        Destroys any existing scene objects first, then creates new ones.
        """
        # Clean up previous level's scene objects
        self._clear_active()

        # Fetch current level data
        level = self._levels[self._current_level_index]

        # Create parking spots
        for i, spot_data in enumerate(level["spots"]):
            spot = ParkingSpot(
                position=Vec3(spot_data["position"]),
                target_rotation=spot_data.get("rotation", 0),
                spot_id=i,
            )
            spot.create_visual()                   # Render in scene
            self._active_spots.append(spot)

        # Create obstacles
        for obs_data in level["obstacles"]:
            obs = Obstacle(
                position=Vec3(obs_data["position"]),
                obstacle_type=obs_data.get("type", "barrier"),
                scale=Vec3(obs_data.get("scale", (1, 1, 1))),
                rotation_y=obs_data.get("rotation", 0),
            )
            obs.create_visual()                    # Render in scene
            self._active_obstacles.append(obs)

    def next_level(self) -> bool:
        """Advance to the next level.

        Returns True if there is a next level, False if the player has
        completed all levels.
        """
        if self._current_level_index + 1 < len(self._levels):
            self._current_level_index += 1
            return True                            # More levels remain
        return False                               # All levels completed

    def reset_to_first(self) -> None:
        """Reset back to level 1."""
        self._current_level_index = 0

    def unload_level(self) -> None:
        """Remove all active scene objects (called on level exit)."""
        self._clear_active()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _clear_active(self) -> None:
        """Destroy all spawned spots and obstacles."""
        for spot in self._active_spots:
            spot.destroy_visual()
        self._active_spots.clear()

        for obs in self._active_obstacles:
            obs.destroy_visual()
        self._active_obstacles.clear()
