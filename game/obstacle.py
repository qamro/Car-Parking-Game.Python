# ==============================================================================
# game/obstacle.py
# ==============================================================================
# Obstacle entities that the player must avoid when parking.
# Demonstrates ENCAPSULATION (private collision state) and simple composition.
# ==============================================================================

import math                                          # Distance calculations
from ursina import Entity, Vec3, color, destroy       # Ursina primitives


class Obstacle:
    """A static obstacle in the parking area (barrier, cone, wall, parked car).

    ENCAPSULATION — collision radius and internal entity are private; external
    code uses check_collision() and never touches internals directly.
    """

    # Class-level colour presets for different obstacle types
    OBSTACLE_COLORS = {
        "barrier": color.rgb(200, 200, 0),       # Yellow safety barrier
        "cone": color.rgb(255, 140, 0),           # Orange traffic cone
        "wall": color.rgb(120, 120, 120),         # Grey concrete wall
        "parked_car": color.rgb(150, 30, 30),     # Dark red parked vehicle
        "pillar": color.rgb(180, 180, 180),       # Grey support pillar
        "dumpster": color.rgb(0, 100, 0),         # Green dumpster
    }

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(
        self,
        position: Vec3,                         # World position
        obstacle_type: str = "barrier",         # Key into OBSTACLE_COLORS
        scale: Vec3 = Vec3(1, 1, 1),            # Dimensions (width, height, depth)
        rotation_y: float = 0.0,                # Yaw rotation
    ) -> None:
        # ENCAPSULATION: all fields are private
        self._position: Vec3 = Vec3(position)
        self._obstacle_type: str = obstacle_type
        self._scale: Vec3 = Vec3(scale)
        self._rotation_y: float = rotation_y
        self._entity: Entity | None = None
        # Collision radius approximated as half the longest horizontal dimension
        self._collision_radius: float = max(scale.x, scale.z) / 2.0 + 0.2

    # ------------------------------------------------------------------
    # Properties (ENCAPSULATION — controlled read access)
    # ------------------------------------------------------------------
    @property
    def position(self) -> Vec3:
        """Return obstacle world position."""
        return Vec3(self._position)

    @property
    def obstacle_type(self) -> str:
        """Return the obstacle type string."""
        return self._obstacle_type

    @property
    def collision_radius(self) -> float:
        """Return the collision radius."""
        return self._collision_radius

    # ------------------------------------------------------------------
    # Scene management
    # ------------------------------------------------------------------
    def create_visual(self) -> None:
        """Spawn the 3-D obstacle entity in the scene."""
        # Choose colour from preset or fall back to grey
        obs_color = self.OBSTACLE_COLORS.get(self._obstacle_type, color.gray)

        if self._obstacle_type == "cone":
            # Traffic cones are taller and narrower
            self._entity = Entity(
                model="cube",
                color=obs_color,
                scale=self._scale,
                position=self._position,
                rotation_y=self._rotation_y,
            )
            # White stripe on the cone
            Entity(
                parent=self._entity,
                model="cube",
                color=color.white,
                scale=(1.05, 0.2, 1.05),             # Slightly wider stripe
                position=(0, 0.3, 0),                # Upper portion
            )
        elif self._obstacle_type == "parked_car":
            # Simplified static car shape
            self._entity = Entity(
                model="cube",
                color=obs_color,
                scale=self._scale,
                position=self._position,
                rotation_y=self._rotation_y,
            )
            # Cabin on top
            Entity(
                parent=self._entity,
                model="cube",
                color=color.rgb(120, 20, 20),
                scale=(0.85, 0.7, 0.5),
                position=(0, 0.7, 0),
            )
        elif self._obstacle_type == "pillar":
            # Cylindrical pillar approximated with a cube
            self._entity = Entity(
                model="cube",
                color=obs_color,
                scale=self._scale,
                position=self._position,
                rotation_y=self._rotation_y,
            )
        else:
            # Default box obstacle (barrier, wall, dumpster)
            self._entity = Entity(
                model="cube",
                color=obs_color,
                scale=self._scale,
                position=self._position,
                rotation_y=self._rotation_y,
            )

            # Add caution stripes to barriers
            if self._obstacle_type == "barrier":
                Entity(
                    parent=self._entity,
                    model="cube",
                    color=color.rgb(40, 40, 40),
                    scale=(1.02, 0.15, 1.02),
                    position=(0, 0.35, 0),
                )

    def destroy_visual(self) -> None:
        """Remove obstacle from the scene."""
        if self._entity:
            destroy(self._entity)
            self._entity = None

    # ------------------------------------------------------------------
    # Collision detection
    # ------------------------------------------------------------------
    def check_collision(self, vehicle_pos: Vec3, vehicle_radius: float) -> bool:
        """Return True if the vehicle overlaps this obstacle.

        Uses simple circle-circle intersection in the XZ plane.
        ENCAPSULATION — callers don't need to know about our internal radius.
        """
        dx = vehicle_pos.x - self._position.x
        dz = vehicle_pos.z - self._position.z
        distance = math.sqrt(dx * dx + dz * dz)
        return distance < (self._collision_radius + vehicle_radius)

    def get_push_direction(self, vehicle_pos: Vec3) -> Vec3:
        """Return a unit vector pointing from obstacle centre → vehicle.

        Used to push the vehicle away on collision (simple resolution).
        """
        dx = vehicle_pos.x - self._position.x
        dz = vehicle_pos.z - self._position.z
        dist = math.sqrt(dx * dx + dz * dz)
        if dist < 0.001:
            return Vec3(1, 0, 0)                # Arbitrary if exactly overlapping
        return Vec3(dx / dist, 0, dz / dist)
