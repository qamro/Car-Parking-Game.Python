# ==============================================================================
# game/camera_controller.py
# ==============================================================================
# Third-person camera that smoothly follows the player's vehicle.
#
# ENCAPSULATION: Camera offsets and smoothing parameters are private; the game
# loop only calls update() each frame.
# ==============================================================================

import math                                        # Trigonometry for orbit
from ursina import camera, Vec3, lerp              # Ursina camera and math


class CameraController:
    """Smooth third-person chase camera.

    ENCAPSULATION — all tuning parameters are private; the public API is just
    update() and reset().
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(
        self,
        distance: float = 12.0,                # Distance behind the vehicle
        height: float = 7.0,                   # Height above the vehicle
        look_height: float = 1.0,              # How high above the car to look at
        smoothness: float = 5.0,               # Interpolation speed (higher = snappier)
    ) -> None:
        # ENCAPSULATION: private tuning attributes
        self._distance: float = distance
        self._height: float = height
        self._look_height: float = look_height
        self._smoothness: float = smoothness
        self._current_position: Vec3 = Vec3(0, height, -distance)  # Camera world pos

    # ------------------------------------------------------------------
    # Properties (ENCAPSULATION)
    # ------------------------------------------------------------------
    @property
    def distance(self) -> float:
        """Return the follow distance."""
        return self._distance

    @distance.setter
    def distance(self, value: float) -> None:
        """Set follow distance (clamped to reasonable range)."""
        self._distance = max(3.0, min(30.0, value))

    @property
    def height(self) -> float:
        """Return the camera height."""
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        """Set camera height (clamped)."""
        self._height = max(2.0, min(20.0, value))

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, target_pos: Vec3, target_rotation_y: float, dt: float) -> None:
        """Move the camera to follow the target vehicle each frame.

        The camera orbits behind the vehicle based on its yaw, then smoothly
        interpolates toward the ideal position to avoid jarring snaps.
        """
        # Calculate ideal camera position: behind and above the vehicle
        rad = math.radians(target_rotation_y)

        # Offset behind the vehicle (negative forward direction)
        ideal_x = target_pos.x - math.sin(rad) * self._distance
        ideal_z = target_pos.z - math.cos(rad) * self._distance
        ideal_y = target_pos.y + self._height

        ideal_position = Vec3(ideal_x, ideal_y, ideal_z)

        # Smooth interpolation toward ideal position
        t = min(1.0, self._smoothness * dt)         # Interpolation factor
        self._current_position = Vec3(
            lerp(self._current_position.x, ideal_position.x, t),
            lerp(self._current_position.y, ideal_position.y, t),
            lerp(self._current_position.z, ideal_position.z, t),
        )

        # Apply to the engine camera
        camera.position = self._current_position

        # Look at a point slightly above the vehicle centre
        look_target = Vec3(
            target_pos.x,
            target_pos.y + self._look_height,
            target_pos.z,
        )
        camera.look_at(look_target)

    def reset(self, target_pos: Vec3, target_rotation_y: float) -> None:
        """Snap the camera to the ideal position instantly (no smoothing).

        Called when a level first loads so there's no initial drift.
        """
        rad = math.radians(target_rotation_y)
        self._current_position = Vec3(
            target_pos.x - math.sin(rad) * self._distance,
            target_pos.y + self._height,
            target_pos.z - math.cos(rad) * self._distance,
        )
        camera.position = self._current_position
        camera.look_at(Vec3(target_pos.x, target_pos.y + self._look_height, target_pos.z))
