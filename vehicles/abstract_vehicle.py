# ==============================================================================
# vehicles/abstract_vehicle.py
# ==============================================================================
# ABSTRACTION: This module defines the AbstractVehicle class using Python's ABC
# (Abstract Base Class) module.  Concrete vehicles (Car, Truck) MUST implement
# every abstract method, guaranteeing a uniform interface while allowing each
# subclass to provide its own behaviour (POLYMORPHISM).
#
# ENCAPSULATION: All internal state (speed, position, rotation, etc.) is stored
# in private attributes (prefixed with underscore) and accessed only through
# public property getters / setters.  This prevents external code from putting
# the vehicle into an invalid state.
# ==============================================================================

from abc import ABC, abstractmethod        # Standard library — Abstract Base Class support
from ursina import Vec3                     # Ursina 3-component vector for 3D positions


class AbstractVehicle(ABC):
    """Abstract base class for all drivable vehicles in the game.

    OOP Principle — ABSTRACTION
    ---------------------------
    By declaring key behaviours as @abstractmethod we define *what* a vehicle
    can do without specifying *how*.  Each concrete subclass fills in the
    implementation details.

    OOP Principle — ENCAPSULATION
    -----------------------------
    Internal physics state is hidden behind underscored attributes and exposed
    via @property decorators so that invariants (e.g. speed >= 0) can be
    enforced inside the setters.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(
        self,
        name: str,                         # Human-readable vehicle identifier
        max_speed: float = 15.0,           # Maximum forward speed (units/sec)
        acceleration_rate: float = 8.0,    # How quickly the vehicle speeds up
        brake_rate: float = 12.0,          # How quickly the vehicle slows down
        turn_speed: float = 80.0,          # Degrees per second at full lock
        mass: float = 1200.0,              # Vehicle mass in kg (affects feel)
    ) -> None:
        # ENCAPSULATION: all attributes are "protected" (single underscore)
        self._name: str = name                         # Vehicle display name
        self._max_speed: float = max_speed             # Speed cap
        self._acceleration_rate: float = acceleration_rate  # Acceleration magnitude
        self._brake_rate: float = brake_rate            # Braking magnitude
        self._turn_speed: float = turn_speed            # Steering sensitivity
        self._mass: float = mass                        # Physics mass
        self._current_speed: float = 0.0                # Current forward speed
        self._position: Vec3 = Vec3(0, 0, 0)            # World-space position
        self._rotation_y: float = 0.0                   # Yaw rotation (degrees)
        self._is_braking: bool = False                   # Whether brakes are applied
        self._health: float = 100.0                      # Collision health

    # ------------------------------------------------------------------
    # Properties (ENCAPSULATION — controlled access to private state)
    # ------------------------------------------------------------------
    @property
    def name(self) -> str:
        """Return the vehicle's display name (read-only)."""
        return self._name

    @property
    def max_speed(self) -> float:
        """Return the vehicle's maximum forward speed."""
        return self._max_speed

    @max_speed.setter
    def max_speed(self, value: float) -> None:
        """Set max speed, enforcing a positive value."""
        # ENCAPSULATION: validate before storing
        self._max_speed = max(0.0, value)

    @property
    def current_speed(self) -> float:
        """Return the vehicle's current speed."""
        return self._current_speed

    @current_speed.setter
    def current_speed(self, value: float) -> None:
        """Set current speed, clamping to [−max_speed/2, max_speed]."""
        # Allow reverse at half max speed
        self._current_speed = max(-self._max_speed * 0.5, min(value, self._max_speed))

    @property
    def position(self) -> Vec3:
        """Return a copy of the vehicle's world position."""
        return Vec3(self._position)

    @position.setter
    def position(self, value: Vec3) -> None:
        """Set the vehicle's world position."""
        self._position = Vec3(value)

    @property
    def rotation_y(self) -> float:
        """Return the vehicle's yaw rotation in degrees."""
        return self._rotation_y

    @rotation_y.setter
    def rotation_y(self, value: float) -> None:
        """Set yaw, wrapping to 0-360 range."""
        self._rotation_y = value % 360.0

    @property
    def is_braking(self) -> bool:
        """Return whether the vehicle is currently braking."""
        return self._is_braking

    @property
    def health(self) -> float:
        """Return the vehicle's remaining health."""
        return self._health

    @health.setter
    def health(self, value: float) -> None:
        """Set health, clamping to [0, 100]."""
        self._health = max(0.0, min(100.0, value))

    @property
    def mass(self) -> float:
        """Return the vehicle mass."""
        return self._mass

    # ------------------------------------------------------------------
    # Abstract methods (ABSTRACTION — subclasses MUST implement these)
    # ------------------------------------------------------------------
    @abstractmethod
    def accelerate(self, dt: float) -> None:
        """Increase the vehicle's speed.  *dt* is the frame delta time."""
        ...

    @abstractmethod
    def brake(self, dt: float) -> None:
        """Decrease the vehicle's speed.  *dt* is the frame delta time."""
        ...

    @abstractmethod
    def steer(self, direction: float, dt: float) -> None:
        """Steer the vehicle.  *direction* is −1 (left) to +1 (right)."""
        ...

    @abstractmethod
    def update_physics(self, dt: float) -> None:
        """Run one physics tick — move the vehicle based on current speed."""
        ...

    @abstractmethod
    def reset(self, position: Vec3, rotation_y: float) -> None:
        """Reset the vehicle to a given position and rotation."""
        ...

    @abstractmethod
    def create_model(self) -> None:
        """Build the 3-D visual representation of this vehicle."""
        ...

    @abstractmethod
    def get_vehicle_type(self) -> str:
        """Return a string identifier for the vehicle type (POLYMORPHISM)."""
        ...

    # ------------------------------------------------------------------
    # Concrete helper (shared logic available to all subclasses)
    # ------------------------------------------------------------------
    def apply_friction(self, dt: float, friction: float = 3.0) -> None:
        """Gradually reduce speed when the player is not accelerating.

        This is a concrete method on the ABC so every subclass inherits the
        same friction model without reimplementing it (INHERITANCE — code reuse).
        """
        if self._current_speed > 0:
            # Reduce positive speed toward zero
            self._current_speed = max(0.0, self._current_speed - friction * dt)
        elif self._current_speed < 0:
            # Reduce negative (reverse) speed toward zero
            self._current_speed = min(0.0, self._current_speed + friction * dt)

    def take_damage(self, amount: float) -> None:
        """Reduce health by *amount* (collision penalty).

        Concrete method shared by all vehicles (INHERITANCE — code reuse).
        """
        self.health = self._health - abs(amount)

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return (
            f"<{self.__class__.__name__}(name={self._name!r}, "
            f"speed={self._current_speed:.1f}, "
            f"pos={self._position})>"
        )
