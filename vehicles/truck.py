# ==============================================================================
# vehicles/truck.py
# ==============================================================================
# INHERITANCE: Truck extends AbstractVehicle, just like Car, but with different
# physics tuning (slower acceleration, wider turning radius, heavier mass).
#
# POLYMORPHISM: Truck overrides every abstract method with truck-specific logic.
# Any code that holds an AbstractVehicle reference can call accelerate() or
# steer() and the correct truck behaviour will execute at runtime, without the
# caller needing to know the concrete type.
# ==============================================================================

import math                                        # Standard math utilities
from ursina import Entity, Vec3, color, destroy     # Ursina engine imports
from vehicles.abstract_vehicle import AbstractVehicle  # Abstract base class


class Truck(AbstractVehicle):
    """A heavy delivery truck — slower but more massive than a Car.

    POLYMORPHISM — same interface as Car, completely different behaviour.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(
        self,
        name: str = "Delivery Truck",       # Display name
        max_speed: float = 12.0,             # Slower top speed than car
        acceleration_rate: float = 5.0,      # Sluggish acceleration
        brake_rate: float = 8.0,             # Heavier, longer braking distance
        turn_speed: float = 55.0,            # Wider turning radius
        mass: float = 3500.0,                # Much heavier than a car
        truck_color: tuple = (0.8, 0.3, 0.1),  # Orange paint
    ) -> None:
        # INHERITANCE: initialise base class state
        super().__init__(name, max_speed, acceleration_rate, brake_rate, turn_speed, mass)

        # ENCAPSULATION: truck-specific private attributes
        self._truck_color: tuple = truck_color
        self._entity: Entity | None = None
        self._wheel_entities: list = []
        self._brake_light_entities: list = []
        self._width: float = 1.3               # Wider than a car
        self._length: float = 3.2              # Longer than a car
        self._steering_angle: float = 0.0

    # ------------------------------------------------------------------
    # Properties (ENCAPSULATION)
    # ------------------------------------------------------------------
    @property
    def entity(self) -> Entity | None:
        """Return the root Ursina entity."""
        return self._entity

    @property
    def width(self) -> float:
        """Return truck body width."""
        return self._width

    @property
    def length(self) -> float:
        """Return truck body length."""
        return self._length

    # ------------------------------------------------------------------
    # POLYMORPHISM: concrete implementations unique to Truck
    # ------------------------------------------------------------------
    def get_vehicle_type(self) -> str:
        """Return 'truck' — runtime type identification."""
        return "truck"

    def create_model(self) -> None:
        """Build a 3-D truck model from primitives.

        POLYMORPHISM — visually and dimensionally different from Car.create_model().
        """
        # Root transform parent
        self._entity = Entity(
            model=None,
            position=self._position,
            rotation_y=self._rotation_y,
        )

        # --- Cab (driver's compartment, front) ---
        Entity(
            parent=self._entity,
            model="cube",
            color=color.rgb(*[int(c * 255) for c in self._truck_color]),
            scale=(self._width, 0.6, self._length * 0.35),
            position=(0, 0.4, self._length * 0.25),
        )

        # --- Cargo box (rear section) ---
        Entity(
            parent=self._entity,
            model="cube",
            color=color.rgb(200, 200, 200),        # Light grey cargo box
            scale=(self._width * 0.95, 0.8, self._length * 0.55),
            position=(0, 0.5, -self._length * 0.15),
        )

        # --- Cab windshield ---
        Entity(
            parent=self._entity,
            model="cube",
            color=color.rgba(150, 200, 255, 180),
            scale=(self._width * 0.85, 0.35, 0.05),
            position=(0, 0.65, self._length * 0.42),
        )

        # --- Headlights ---
        for side in (-1, 1):
            Entity(
                parent=self._entity,
                model="cube",
                color=color.rgb(255, 255, 200),
                scale=(0.18, 0.12, 0.05),
                position=(side * 0.45, 0.35, self._length / 2 + 0.01),
            )

        # --- Brake / tail lights ---
        self._brake_light_entities = []
        for side in (-1, 1):
            bl = Entity(
                parent=self._entity,
                model="cube",
                color=color.rgb(100, 0, 0),
                scale=(0.18, 0.12, 0.05),
                position=(side * 0.45, 0.35, -(self._length / 2 + 0.01)),
            )
            self._brake_light_entities.append(bl)

        # --- Wheels (6 wheels: 2 front, 4 rear for a realistic truck) ---
        self._wheel_entities = []
        wheel_positions = [
            (-self._width / 2 - 0.08, 0.12, self._length * 0.3),   # Front-left
            (self._width / 2 + 0.08, 0.12, self._length * 0.3),    # Front-right
            (-self._width / 2 - 0.08, 0.12, -self._length * 0.2),  # Mid-rear-left
            (self._width / 2 + 0.08, 0.12, -self._length * 0.2),   # Mid-rear-right
            (-self._width / 2 - 0.08, 0.12, -self._length * 0.38), # Rear-left
            (self._width / 2 + 0.08, 0.12, -self._length * 0.38),  # Rear-right
        ]
        for wx, wy, wz in wheel_positions:
            wheel = Entity(
                parent=self._entity,
                model="cube",
                color=color.dark_gray,
                scale=(0.12, 0.24, 0.3),
                position=(wx, wy, wz),
            )
            self._wheel_entities.append(wheel)

    # ------------------------------------------------------------------
    # Physics (POLYMORPHISM — truck-specific tuning)
    # ------------------------------------------------------------------
    def accelerate(self, dt: float) -> None:
        """Accelerate the truck — noticeably slower than a car.

        POLYMORPHISM — same method signature, different acceleration feel.
        """
        self._is_braking = False
        self._current_speed = min(
            self._current_speed + self._acceleration_rate * dt,
            self._max_speed,
        )

    def brake(self, dt: float) -> None:
        """Brake the truck — longer stopping distance due to mass.

        POLYMORPHISM — truck brakes are weaker than car brakes.
        """
        self._is_braking = True
        self._current_speed = max(
            self._current_speed - self._brake_rate * dt,
            -self._max_speed * 0.3,          # Reverse limited to 30 % for trucks
        )

    def steer(self, direction: float, dt: float) -> None:
        """Steer the truck — wider turning radius than a car.

        POLYMORPHISM — same interface, but the truck feels heavier and less agile.
        """
        if abs(self._current_speed) < 0.3:
            return                           # Can't steer while stationary

        # Speed factor for stability at high speed
        speed_factor = min(abs(self._current_speed) / self._max_speed, 1.0)
        effective_turn = self._turn_speed * speed_factor * direction * dt

        if self._current_speed < 0:
            effective_turn = -effective_turn  # Invert when reversing

        self._rotation_y += effective_turn
        self._steering_angle = direction * 20.0  # Smaller visual wheel turn

    def update_physics(self, dt: float) -> None:
        """Move the truck forward along its heading.

        Identical algorithm to Car, but operates on the truck's own state
        (different speed / turn values make the feel distinct).
        """
        rad = math.radians(self._rotation_y)
        forward_x = math.sin(rad)
        forward_z = math.cos(rad)

        self._position.x += forward_x * self._current_speed * dt
        self._position.z += forward_z * self._current_speed * dt
        self._position.y = 0

        if self._entity:
            self._entity.position = self._position
            self._entity.rotation_y = self._rotation_y

            # Front-wheel steering visuals
            if len(self._wheel_entities) >= 2:
                self._wheel_entities[0].rotation_y = self._steering_angle
                self._wheel_entities[1].rotation_y = self._steering_angle

            for bl in self._brake_light_entities:
                bl.color = color.rgb(255, 0, 0) if self._is_braking else color.rgb(100, 0, 0)

    def reset(self, position: Vec3, rotation_y: float) -> None:
        """Reset truck state for a level restart."""
        self._position = Vec3(position)
        self._rotation_y = rotation_y
        self._current_speed = 0.0
        self._is_braking = False
        self._health = 100.0
        self._steering_angle = 0.0

        if self._entity:
            self._entity.position = self._position
            self._entity.rotation_y = self._rotation_y

    def destroy_model(self) -> None:
        """Remove the truck from the scene."""
        if self._entity:
            destroy(self._entity)
            self._entity = None
