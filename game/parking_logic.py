# ==============================================================================
# game/parking_logic.py
# ==============================================================================
# ABSTRACTION: AbstractParkingSpot defines the interface for all parking spots
# using Python's ABC.  The concrete ParkingSpot class implements the detection
# and scoring logic.
#
# ENCAPSULATION: Internal accuracy calculations and state are hidden behind
# property accessors.
#
# INHERITANCE: ParkingSpot inherits from AbstractParkingSpot.
# ==============================================================================

from abc import ABC, abstractmethod          # Abstract Base Class support
import math                                  # Math utilities for distance calc
from ursina import Entity, Vec3, color, destroy  # Ursina engine primitives


class AbstractParkingSpot(ABC):
    """Abstract base class for parking spot detection.

    ABSTRACTION — declares *what* a parking spot must do (check occupancy,
    calculate accuracy) without specifying *how*.
    """

    @abstractmethod
    def is_vehicle_parked(self, vehicle_pos: Vec3, vehicle_rot: float) -> bool:
        """Return True if the vehicle is considered parked in this spot."""
        ...

    @abstractmethod
    def calculate_accuracy(self, vehicle_pos: Vec3, vehicle_rot: float) -> float:
        """Return a 0-100 accuracy score for how well the vehicle is parked."""
        ...

    @abstractmethod
    def create_visual(self) -> None:
        """Draw the parking spot indicator in the 3-D scene."""
        ...

    @abstractmethod
    def destroy_visual(self) -> None:
        """Remove the parking spot indicator from the scene."""
        ...


class ParkingSpot(AbstractParkingSpot):
    """Concrete parking spot with position, rotation, and tolerance settings.

    INHERITANCE — extends AbstractParkingSpot with full implementation.
    ENCAPSULATION — internal thresholds and entity references are private.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(
        self,
        position: Vec3,                          # World position of the spot centre
        target_rotation: float = 0.0,            # Expected vehicle yaw (degrees)
        width: float = 1.6,                      # Spot width (slightly wider than car)
        length: float = 3.0,                     # Spot length (slightly longer than car)
        position_tolerance: float = 1.2,         # Max distance from centre for "parked"
        rotation_tolerance: float = 25.0,        # Max rotation error (degrees)
        spot_id: int = 0,                        # Unique identifier for this spot
    ) -> None:
        # ENCAPSULATION: private internal state
        self._position: Vec3 = Vec3(position)
        self._target_rotation: float = target_rotation
        self._width: float = width
        self._length: float = length
        self._position_tolerance: float = position_tolerance
        self._rotation_tolerance: float = rotation_tolerance
        self._spot_id: int = spot_id
        self._is_occupied: bool = False          # Whether a vehicle is currently parked
        self._entity: Entity | None = None       # Visual indicator entity
        self._border_entities: list = []         # Line markers around the spot

    # ------------------------------------------------------------------
    # Properties (ENCAPSULATION)
    # ------------------------------------------------------------------
    @property
    def position(self) -> Vec3:
        """Return the centre position of this parking spot."""
        return Vec3(self._position)

    @property
    def target_rotation(self) -> float:
        """Return the expected vehicle rotation for a perfect park."""
        return self._target_rotation

    @property
    def is_occupied(self) -> bool:
        """Return whether a vehicle is currently parked here."""
        return self._is_occupied

    @property
    def spot_id(self) -> int:
        """Return the spot's unique identifier."""
        return self._spot_id

    # ------------------------------------------------------------------
    # Abstract method implementations (INHERITANCE + POLYMORPHISM)
    # ------------------------------------------------------------------
    def is_vehicle_parked(self, vehicle_pos: Vec3, vehicle_rot: float) -> bool:
        """Check if a vehicle at the given position/rotation is parked here.

        A vehicle counts as "parked" when:
        1. Its centre is within position_tolerance of the spot centre.
        2. Its yaw is within rotation_tolerance of the target rotation.

        INHERITANCE — fulfils the contract from AbstractParkingSpot.
        """
        # Horizontal distance between vehicle and spot centre
        dx = vehicle_pos.x - self._position.x
        dz = vehicle_pos.z - self._position.z
        distance = math.sqrt(dx * dx + dz * dz)

        # Check position tolerance
        if distance > self._position_tolerance:
            self._is_occupied = False
            return False

        # Normalise rotation difference to [-180, 180]
        rot_diff = abs((vehicle_rot - self._target_rotation + 180) % 360 - 180)

        # Also accept 180-degree-flipped orientation (front-in or back-in)
        rot_diff_flipped = abs((vehicle_rot - self._target_rotation + 360) % 360 - 180)
        rot_diff = min(rot_diff, rot_diff_flipped)

        # Check rotation tolerance
        if rot_diff > self._rotation_tolerance:
            self._is_occupied = False
            return False

        # Vehicle is within both tolerances — it's parked!
        self._is_occupied = True
        return True

    def calculate_accuracy(self, vehicle_pos: Vec3, vehicle_rot: float) -> float:
        """Score parking accuracy from 0 (terrible) to 100 (perfect).

        Position accounts for 60 % and rotation for 40 % of the total score.
        """
        # --- Position score (60 %) ---
        dx = vehicle_pos.x - self._position.x
        dz = vehicle_pos.z - self._position.z
        distance = math.sqrt(dx * dx + dz * dz)
        # Perfect = 0 distance → 60 pts; tolerance edge → 0 pts
        pos_score = max(0.0, (1.0 - distance / self._position_tolerance)) * 60.0

        # --- Rotation score (40 %) ---
        rot_diff = abs((vehicle_rot - self._target_rotation + 180) % 360 - 180)
        rot_diff_flipped = abs((vehicle_rot - self._target_rotation + 360) % 360 - 180)
        rot_diff = min(rot_diff, rot_diff_flipped)
        rot_score = max(0.0, (1.0 - rot_diff / self._rotation_tolerance)) * 40.0

        return round(pos_score + rot_score, 1)

    def create_visual(self) -> None:
        """Draw parking-spot lines on the ground.

        Creates a semi-transparent green rectangle with white border lines
        to indicate where the player should park.
        """
        # Ground fill — translucent green
        self._entity = Entity(
            model="quad",                            # Flat plane
            color=color.rgba(0, 255, 0, 60),         # Semi-transparent green
            scale=(self._width, self._length),       # Parking-spot dimensions
            position=(self._position.x, 0.02, self._position.z),  # Just above ground
            rotation_x=90,                           # Lay flat
            rotation_y=self._target_rotation,        # Align with expected heading
        )

        # Border lines (white) — four edges of the rectangle
        self._border_entities = []
        half_w = self._width / 2
        half_l = self._length / 2
        line_thickness = 0.06                         # Thin white lines

        # Define border segments as (scale, local_offset)
        borders = [
            ((self._width, line_thickness), (0, half_l)),        # Front edge
            ((self._width, line_thickness), (0, -half_l)),       # Rear edge
            ((line_thickness, self._length), (-half_w, 0)),      # Left edge
            ((line_thickness, self._length), (half_w, 0)),       # Right edge
        ]

        rot_rad = math.radians(self._target_rotation)
        cos_r = math.cos(rot_rad)
        sin_r = math.sin(rot_rad)

        for (sw, sl), (lx, lz) in borders:
            # Rotate local offset by spot rotation to get world offset
            wx = lx * cos_r - lz * sin_r
            wz = lx * sin_r + lz * cos_r

            border = Entity(
                model="quad",
                color=color.white,
                scale=(sw, sl),
                position=(
                    self._position.x + wx,
                    0.03,                             # Slightly above fill
                    self._position.z + wz,
                ),
                rotation_x=90,
                rotation_y=self._target_rotation,
            )
            self._border_entities.append(border)

        # Directional arrow to show which way to face
        arrow = Entity(
            model="quad",
            color=color.rgba(255, 255, 255, 120),
            scale=(0.3, 0.6),
            position=(
                self._position.x + math.sin(rot_rad) * 0.4,
                0.04,
                self._position.z + math.cos(rot_rad) * 0.4,
            ),
            rotation_x=90,
            rotation_y=self._target_rotation,
        )
        self._border_entities.append(arrow)

    def destroy_visual(self) -> None:
        """Remove parking-spot visuals from the scene."""
        if self._entity:
            destroy(self._entity)
            self._entity = None
        for b in self._border_entities:
            destroy(b)
        self._border_entities.clear()

    def set_highlight(self, active: bool) -> None:
        """Change the spot colour to indicate proximity.

        Green = available, Yellow = vehicle nearby but not parked.
        """
        if self._entity:
            if active:
                self._entity.color = color.rgba(255, 255, 0, 80)   # Yellow highlight
            else:
                self._entity.color = color.rgba(0, 255, 0, 60)     # Default green
