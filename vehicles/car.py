# ==============================================================================
# vehicles/car.py
# ==============================================================================
# INHERITANCE: Car extends AbstractVehicle, inheriting shared state and helpers
# (apply_friction, take_damage) while providing its own implementations of every
# abstract method.
#
# POLYMORPHISM: Car overrides get_vehicle_type(), accelerate(), brake(), steer(),
# and create_model() with car-specific behaviour.  Code that works with an
# AbstractVehicle reference can call these methods and get the correct car
# behaviour at runtime (dynamic dispatch).
#
# ENCAPSULATION: The 3-D entity and internal physics details are hidden; outside
# code interacts only through the public interface defined on the base class.
# ==============================================================================

import math                                        # Standard math utilities
from ursina import (                               # Ursina engine imports
    Entity, Vec3, color, held_keys, destroy,
)
from vehicles.abstract_vehicle import AbstractVehicle  # Our abstract base class


class Car(AbstractVehicle):
    """A standard sedan-style car.

    INHERITANCE — extends AbstractVehicle with car-specific physics and visuals.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(
        self,
        name: str = "Sedan",                   # Display name for this car
        max_speed: float = 18.0,               # Top speed (units / sec)
        acceleration_rate: float = 10.0,       # How fast we speed up
        brake_rate: float = 14.0,              # How fast we slow down
        turn_speed: float = 90.0,              # Steering degrees / sec
        mass: float = 1200.0,                  # Mass in kg
        car_color: tuple = (0.2, 0.4, 0.9),   # RGB body colour
    ) -> None:
        # INHERITANCE: call the parent constructor to initialise shared state
        super().__init__(name, max_speed, acceleration_rate, brake_rate, turn_speed, mass)

        # ENCAPSULATION: car-specific private attributes
        self._car_color: tuple = car_color      # Body paint colour
        self._entity: Entity | None = None      # Root Ursina entity (built later)
        self._wheel_entities: list = []          # References to wheel meshes
        self._brake_light_entities: list = []    # References to brake light meshes
        self._width: float = 1.0                # Car width for collision sizing
        self._length: float = 2.2               # Car length for collision sizing
        self._steering_angle: float = 0.0       # Visual steering wheel angle

    # ------------------------------------------------------------------
    # Property getters for car-specific state (ENCAPSULATION)
    # ------------------------------------------------------------------
    @property
    def entity(self) -> Entity | None:
        """Return the root Ursina entity."""
        return self._entity

    @property
    def width(self) -> float:
        """Return car body width."""
        return self._width

    @property
    def length(self) -> float:
        """Return car body length."""
        return self._length

    # ------------------------------------------------------------------
    # POLYMORPHISM: concrete implementations of abstract methods
    # ------------------------------------------------------------------
    def get_vehicle_type(self) -> str:
        """Return 'car' — identifies this vehicle type at runtime."""
        return "car"

    def create_model(self) -> None:
        """Build a 3-D car model from primitive shapes.

        POLYMORPHISM — each vehicle subclass constructs a visually distinct
        model while honouring the same create_model() interface.
        """
        # Root entity acts as the transform parent for all car parts
        self._entity = Entity(
            model=None,                     # No mesh on the root itself
            position=self._position,        # Start at initial position
            rotation_y=self._rotation_y,    # Start at initial yaw
        )

        # --- Car body (main chassis) ---
        body = Entity(
            parent=self._entity,             # Attach to root
            model="cube",                    # Simple box primitive
            color=color.rgb(*[int(c * 255) for c in self._car_color]),  # Paint colour
            scale=(self._width, 0.35, self._length),  # Width, height, length
            position=(0, 0.25, 0),           # Slightly above ground
        )

        # --- Cabin (windowed upper section) ---
        cabin = Entity(
            parent=self._entity,
            model="cube",
            color=color.rgb(
                int(self._car_color[0] * 200),
                int(self._car_color[1] * 200),
                int(self._car_color[2] * 200),
            ),
            scale=(self._width * 0.85, 0.3, self._length * 0.5),  # Slightly narrower
            position=(0, 0.55, -0.1),        # On top of the body, shifted back
        )

        # --- Windshield (front glass) ---
        Entity(
            parent=self._entity,
            model="cube",
            color=color.rgba(150, 200, 255, 180),  # Translucent blue
            scale=(self._width * 0.8, 0.25, 0.05),
            position=(0, 0.55, 0.45),        # Front of the cabin
        )

        # --- Rear window ---
        Entity(
            parent=self._entity,
            model="cube",
            color=color.rgba(150, 200, 255, 180),
            scale=(self._width * 0.8, 0.25, 0.05),
            position=(0, 0.55, -0.6),        # Back of the cabin
        )

        # --- Headlights (front) ---
        for side in (-1, 1):                 # Left and right
            Entity(
                parent=self._entity,
                model="cube",
                color=color.rgb(255, 255, 200),  # Warm white
                scale=(0.15, 0.1, 0.05),
                position=(side * 0.35, 0.3, self._length / 2 + 0.01),
            )

        # --- Brake / tail lights (rear) ---
        self._brake_light_entities = []
        for side in (-1, 1):
            bl = Entity(
                parent=self._entity,
                model="cube",
                color=color.rgb(100, 0, 0),      # Dark red when off
                scale=(0.15, 0.1, 0.05),
                position=(side * 0.35, 0.3, -(self._length / 2 + 0.01)),
            )
            self._brake_light_entities.append(bl)  # Keep reference for braking glow

        # --- Wheels (4 corners) ---
        self._wheel_entities = []
        wheel_positions = [
            (-self._width / 2 - 0.05, 0.1, 0.6),   # Front-left
            (self._width / 2 + 0.05, 0.1, 0.6),     # Front-right
            (-self._width / 2 - 0.05, 0.1, -0.6),   # Rear-left
            (self._width / 2 + 0.05, 0.1, -0.6),    # Rear-right
        ]
        for wx, wy, wz in wheel_positions:
            wheel = Entity(
                parent=self._entity,
                model="cube",
                color=color.dark_gray,               # Tyre colour
                scale=(0.1, 0.2, 0.25),              # Thin, tall, short
                position=(wx, wy, wz),
            )
            self._wheel_entities.append(wheel)

        # --- Bumpers ---
        for z_pos in (self._length / 2 + 0.02, -(self._length / 2 + 0.02)):
            Entity(
                parent=self._entity,
                model="cube",
                color=color.rgb(60, 60, 60),
                scale=(self._width * 0.95, 0.08, 0.06),
                position=(0, 0.12, z_pos),
            )

    # ------------------------------------------------------------------
    # Physics methods (POLYMORPHISM — car-specific implementations)
    # ------------------------------------------------------------------
    def accelerate(self, dt: float) -> None:
        """Increase forward speed using the car's acceleration rate.

        POLYMORPHISM — Car accelerates faster than Truck due to different rates.
        """
        self._is_braking = False                # Not braking while accelerating
        # Increase speed toward max, scaled by delta time
        self._current_speed = min(
            self._current_speed + self._acceleration_rate * dt,
            self._max_speed,
        )

    def brake(self, dt: float) -> None:
        """Decrease speed (or reverse) using the car's brake rate.

        POLYMORPHISM — Car brakes more sharply than Truck.
        """
        self._is_braking = True                 # Flag for brake-light visuals
        # Reduce speed; allow negative for reversing
        self._current_speed = max(
            self._current_speed - self._brake_rate * dt,
            -self._max_speed * 0.4,             # Reverse capped at 40 % of max
        )

    def steer(self, direction: float, dt: float) -> None:
        """Rotate the car left or right based on current speed.

        Steering is speed-dependent: slower movement = tighter turning radius,
        which mimics real car behaviour.

        POLYMORPHISM — Car turns faster than Truck.
        """
        if abs(self._current_speed) < 0.3:
            return                               # Cannot steer while stationary

        # Speed factor: steer less at very high speed for stability
        speed_factor = min(abs(self._current_speed) / self._max_speed, 1.0)
        # Effective turn rate
        effective_turn = self._turn_speed * speed_factor * direction * dt

        # Invert steering direction when reversing
        if self._current_speed < 0:
            effective_turn = -effective_turn

        # Apply yaw rotation
        self._rotation_y += effective_turn

        # Update visual steering angle for front wheels
        self._steering_angle = direction * 25.0  # Max 25 degrees visual turn

    def update_physics(self, dt: float) -> None:
        """Move the car forward along its heading and sync the Ursina entity.

        This is called every frame to advance the simulation.
        """
        # Convert yaw to radians for trig
        rad = math.radians(self._rotation_y)

        # Forward vector based on current heading
        forward_x = math.sin(rad)              # X component
        forward_z = math.cos(rad)              # Z component

        # Update position
        self._position.x += forward_x * self._current_speed * dt
        self._position.z += forward_z * self._current_speed * dt

        # Keep car on the ground plane
        self._position.y = 0

        # Sync the Ursina entity with our internal physics state
        if self._entity:
            self._entity.position = self._position
            self._entity.rotation_y = self._rotation_y

            # Rotate front wheels to show steering
            if len(self._wheel_entities) >= 2:
                self._wheel_entities[0].rotation_y = self._steering_angle
                self._wheel_entities[1].rotation_y = self._steering_angle

            # Brake lights glow bright red while braking
            for bl in self._brake_light_entities:
                if self._is_braking:
                    bl.color = color.rgb(255, 0, 0)    # Bright red
                else:
                    bl.color = color.rgb(100, 0, 0)    # Dim red

    def reset(self, position: Vec3, rotation_y: float) -> None:
        """Reset the car to a specific position and rotation.

        Used when restarting a level or respawning after a collision.
        """
        self._position = Vec3(position)         # Copy position
        self._rotation_y = rotation_y            # Set yaw
        self._current_speed = 0.0                # Stop movement
        self._is_braking = False                 # Clear braking flag
        self._health = 100.0                     # Restore health
        self._steering_angle = 0.0               # Centre steering

        # Sync entity visuals
        if self._entity:
            self._entity.position = self._position
            self._entity.rotation_y = self._rotation_y

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def destroy_model(self) -> None:
        """Remove the 3-D model from the scene."""
        if self._entity:
            destroy(self._entity)
            self._entity = None
