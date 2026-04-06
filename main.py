# ==============================================================================
# main.py — 3D Car Parking Game
# ==============================================================================
# Entry point and game loop.  This module wires together every subsystem:
#
#   - Vehicle classes      (ABSTRACTION, INHERITANCE, POLYMORPHISM, ENCAPSULATION)
#   - Parking logic        (ABSTRACTION, INHERITANCE)
#   - Obstacles            (ENCAPSULATION)
#   - Level management     (ENCAPSULATION)
#   - Score tracking       (ENCAPSULATION)
#   - Camera controller    (ENCAPSULATION)
#   - HUD and menus        (ENCAPSULATION)
#
# The game follows a state-machine pattern:
#   MENU → PLAYING → PAUSED / LEVEL_COMPLETE / GAME_OVER → …
#
# Run with:  python main.py
# ==============================================================================

# ── Standard library ─────────────────────────────────────────────────────────
import math                                          # Trig for ground grid
import sys                                           # sys.exit for clean shutdown

# ── Ursina engine ─────────────────────────────────────────────────────────────
from ursina import (
    Ursina,                                          # Application class
    Entity,                                          # Base scene object
    Vec3,                                            # 3-component vector
    color,                                           # Colour helpers
    held_keys,                                       # Keyboard polling dict
    time as ursina_time,                              # Frame delta time
    camera,                                          # Global camera reference
    application,                                     # App-level controls
    destroy,                                         # Remove entities
    window,                                          # Window settings
    DirectionalLight,                                # Scene lighting
    AmbientLight,                                    # Scene ambient light
    Sky,                                             # Skybox
)

# ── Project modules ───────────────────────────────────────────────────────────
from vehicles.car import Car                         # INHERITANCE: Car ← AbstractVehicle
from vehicles.truck import Truck                     # INHERITANCE: Truck ← AbstractVehicle
from vehicles.abstract_vehicle import AbstractVehicle  # ABSTRACTION base type
from game.level_manager import LevelManager          # Level data & scene management
from game.score_manager import ScoreManager          # Score tracking
from game.camera_controller import CameraController  # Third-person chase camera
from ui.hud import HUD                               # Heads-up display
from ui.menu import Menu                             # Menu overlays


# ==============================================================================
# Game States (simple enum-like constants)
# ==============================================================================
STATE_MENU = "menu"                                  # Title screen
STATE_PLAYING = "playing"                            # Active gameplay
STATE_PAUSED = "paused"                              # Pause overlay
STATE_LEVEL_COMPLETE = "level_complete"              # Level finished overlay
STATE_GAME_OVER = "game_over"                        # Time ran out


# ==============================================================================
# ParkingGame — main controller class
# ==============================================================================
class ParkingGame:
    """Top-level game controller.

    Manages the game state machine, creates subsystems, and runs the per-frame
    update loop.

    ENCAPSULATION — all game state and subsystem references are private.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(self) -> None:
        # ENCAPSULATION: private subsystem references
        self._state: str = STATE_MENU                # Current game state

        # Subsystems (created in setup)
        self._level_manager: LevelManager = LevelManager()
        self._score_manager: ScoreManager = ScoreManager()
        self._camera_controller: CameraController = CameraController()
        self._hud: HUD = HUD()
        self._menu: Menu = Menu()

        # POLYMORPHISM: list of available vehicle types — all are AbstractVehicle
        self._vehicle_types: list[type] = [Car, Truck]
        self._current_vehicle_index: int = 0         # Index into _vehicle_types
        self._vehicle: AbstractVehicle | None = None # Active vehicle instance

        # Scene objects
        self._ground: Entity | None = None           # Ground plane
        self._ground_lines: list[Entity] = []        # Grid lines on the ground
        self._environment_entities: list[Entity] = []  # Decorative objects
        self._sky: Entity | None = None              # Skybox

        # Collision cooldown to avoid rapid-fire penalty
        self._collision_cooldown: float = 0.0

        # Parking detection timer — vehicle must stay parked for 1.5 s
        self._park_timer: float = 0.0
        self._park_threshold: float = 1.5            # Seconds to confirm park
        self._all_spots_parked: bool = False          # Whether all spots are satisfied

        # Vehicle switch cooldown
        self._switch_cooldown: float = 0.0

    # ------------------------------------------------------------------
    # Setup (called once after Ursina app is created)
    # ------------------------------------------------------------------
    def setup(self) -> None:
        """Initialise the entire game: scene, menus, HUD."""
        # Configure window
        window.title = "3D Car Parking Game"
        window.borderless = False
        window.exit_button.visible = False           # Hide default exit button
        window.fps_counter.enabled = True            # Show FPS counter

        # Disable default camera controller so we use our own
        camera.orthographic = False
        camera.fov = 60

        # Create persistent scene elements
        self._create_environment()

        # Create HUD (hidden until gameplay starts)
        self._hud.create()
        self._hud.hide()

        # Register menu callbacks
        self._menu.set_callbacks(
            on_start=self._start_game,
            on_resume=self._resume_game,
            on_restart=self._restart_level,
            on_next_level=self._next_level,
            on_quit=self._go_to_menu,
        )

        # Show the main menu
        self._menu.show_main_menu()

    # ------------------------------------------------------------------
    # Environment creation
    # ------------------------------------------------------------------
    def _create_environment(self) -> None:
        """Build the ground plane, grid lines, sky, and lighting."""
        # Ground plane — large dark grey surface
        self._ground = Entity(
            model="plane",
            color=color.rgb(50, 50, 55),
            scale=(80, 1, 80),                       # 80 × 80 units
            position=(0, 0, 0),
            collider=None,
        )

        # Grid lines for visual reference
        self._ground_lines = []
        grid_range = 40                              # Half-size of the grid
        line_spacing = 4                             # Units between lines
        for i in range(-grid_range, grid_range + 1, line_spacing):
            # Lines along X axis
            line_x = Entity(
                model="cube",
                color=color.rgb(65, 65, 70),
                scale=(80, 0.01, 0.04),
                position=(0, 0.005, i),
            )
            self._ground_lines.append(line_x)
            # Lines along Z axis
            line_z = Entity(
                model="cube",
                color=color.rgb(65, 65, 70),
                scale=(0.04, 0.01, 80),
                position=(i, 0.005, 0),
            )
            self._ground_lines.append(line_z)

        # Road markings — center line of a "road" leading to parking area
        for z in range(-30, 30, 3):
            dash = Entity(
                model="cube",
                color=color.rgb(200, 200, 0),        # Yellow dashed centre line
                scale=(0.08, 0.01, 1.5),
                position=(0, 0.006, z),
            )
            self._environment_entities.append(dash)

        # Decorative boundary walls (far edges)
        for pos, sc in [
            ((-38, 0.5, 0), (0.5, 1, 80)),          # Left wall
            ((38, 0.5, 0), (0.5, 1, 80)),            # Right wall
            ((0, 0.5, 38), (80, 1, 0.5)),            # Far wall
            ((0, 0.5, -38), (80, 1, 0.5)),           # Near wall
        ]:
            wall = Entity(
                model="cube",
                color=color.rgb(80, 80, 85),
                scale=sc,
                position=pos,
            )
            self._environment_entities.append(wall)

        # Lamp posts (decorative pillars with "light" cubes)
        lamp_positions = [(-12, 0, -12), (12, 0, -12), (-12, 0, 12), (12, 0, 12)]
        for lx, ly, lz in lamp_positions:
            # Pole
            pole = Entity(
                model="cube",
                color=color.rgb(100, 100, 100),
                scale=(0.15, 3, 0.15),
                position=(lx, 1.5, lz),
            )
            self._environment_entities.append(pole)
            # Light bulb
            bulb = Entity(
                model="cube",
                color=color.rgb(255, 255, 200),
                scale=(0.3, 0.15, 0.3),
                position=(lx, 3.1, lz),
            )
            self._environment_entities.append(bulb)

        # Sky
        self._sky = Sky(color=color.rgb(30, 30, 50))   # Dark evening sky

        # Lighting — directional "sun" light
        DirectionalLight(
            y=10,
            rotation=(45, 45, 0),
        )

    # ------------------------------------------------------------------
    # Vehicle management (POLYMORPHISM — type selected at runtime)
    # ------------------------------------------------------------------
    def _create_vehicle(self) -> None:
        """Instantiate the currently selected vehicle type.

        POLYMORPHISM — the vehicle type is chosen from _vehicle_types at runtime.
        All subsequent code uses the AbstractVehicle interface, so it works
        identically whether the concrete type is Car or Truck.
        """
        # Destroy existing vehicle model if any
        if self._vehicle is not None:
            self._vehicle.destroy_model()

        # Pick the class from the list (POLYMORPHISM: dynamic type selection)
        VehicleClass = self._vehicle_types[self._current_vehicle_index]

        # Instantiate — each subclass has its own default parameters
        self._vehicle = VehicleClass()

        # Position at the level's spawn point
        spawn_pos = self._level_manager.spawn_position
        spawn_rot = self._level_manager.spawn_rotation
        self._vehicle.reset(spawn_pos, spawn_rot)

        # Build the 3-D model (POLYMORPHISM: each class builds a different mesh)
        self._vehicle.create_model()

        # Snap camera to the new vehicle
        self._camera_controller.reset(spawn_pos, spawn_rot)

    def _switch_vehicle(self) -> None:
        """Cycle to the next vehicle type.

        POLYMORPHISM — we swap the concrete type while the rest of the game
        continues using the AbstractVehicle interface unchanged.
        """
        if self._switch_cooldown > 0:
            return                                   # Prevent rapid switching

        # Cycle index
        self._current_vehicle_index = (
            (self._current_vehicle_index + 1) % len(self._vehicle_types)
        )
        self._create_vehicle()
        self._switch_cooldown = 0.5                  # Half-second cooldown

        # Show a brief message
        self._hud.show_message(
            f"Vehicle: {self._vehicle.get_vehicle_type().title()}", color.cyan
        )

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------
    def _start_game(self) -> None:
        """Transition from MENU → PLAYING (level 1)."""
        self._menu.hide_all()
        self._level_manager.reset_to_first()
        self._score_manager.reset_all()
        self._load_current_level()
        self._state = STATE_PLAYING

    def _resume_game(self) -> None:
        """Transition from PAUSED → PLAYING."""
        self._menu.hide_pause_menu()
        self._hud.show()
        self._hud.clear_message()
        self._state = STATE_PLAYING

    def _restart_level(self) -> None:
        """Reload the current level from scratch."""
        self._menu.hide_all()
        self._score_manager.reset_level()
        self._load_current_level()
        self._state = STATE_PLAYING

    def _next_level(self) -> None:
        """Advance to the next level."""
        self._menu.hide_all()
        has_next = self._level_manager.next_level()
        if has_next:
            self._score_manager.reset_level()
            self._load_current_level()
            self._state = STATE_PLAYING
        else:
            # All levels done — return to menu
            self._go_to_menu()

    def _go_to_menu(self) -> None:
        """Return to the main menu."""
        self._menu.hide_all()
        self._hud.hide()
        self._level_manager.unload_level()
        if self._vehicle:
            self._vehicle.destroy_model()
            self._vehicle = None
        self._state = STATE_MENU
        self._menu.show_main_menu()

    # ------------------------------------------------------------------
    # Level loading
    # ------------------------------------------------------------------
    def _load_current_level(self) -> None:
        """Set up the current level: spawn vehicle, load scene, start timer."""
        # Load level scene objects (spots + obstacles)
        self._level_manager.load_level()

        # Create (or recreate) the vehicle at the spawn point
        self._create_vehicle()

        # Start the score timer
        self._score_manager.start_timer(self._level_manager.time_limit)

        # Update HUD
        self._hud.show()
        self._hud.clear_message()
        self._hud.update_level(
            self._level_manager.current_level_number,
            self._level_manager.level_name,
        )
        self._hud.update_score(self._score_manager.total_score)
        self._hud.update_collisions(0)

        # Reset parking timer
        self._park_timer = 0.0
        self._all_spots_parked = False
        self._collision_cooldown = 0.0

    # ------------------------------------------------------------------
    # Per-frame update (called by Ursina every frame)
    # ------------------------------------------------------------------
    def update(self) -> None:
        """Main game loop tick — called automatically by Ursina."""
        # Frame delta time
        dt = ursina_time.dt

        # Reduce cooldowns
        if self._collision_cooldown > 0:
            self._collision_cooldown -= dt
        if self._switch_cooldown > 0:
            self._switch_cooldown -= dt

        # State-specific logic
        if self._state == STATE_PLAYING:
            self._update_playing(dt)
        # Other states are event-driven (menu clicks), no per-frame work needed

    def _update_playing(self, dt: float) -> None:
        """Per-frame logic during active gameplay."""
        if self._vehicle is None:
            return                                   # Safety check

        # ── Input handling ────────────────────────────────────────────
        is_accelerating = False
        is_braking = False
        steer_dir = 0.0

        # Forward / accelerate
        if held_keys["w"] or held_keys["up arrow"]:
            self._vehicle.accelerate(dt)             # POLYMORPHISM: correct impl called
            is_accelerating = True

        # Reverse / brake
        if held_keys["s"] or held_keys["down arrow"]:
            self._vehicle.brake(dt)                  # POLYMORPHISM: correct impl called
            is_braking = True

        # Steer left
        if held_keys["a"] or held_keys["left arrow"]:
            steer_dir = -1.0

        # Steer right
        if held_keys["d"] or held_keys["right arrow"]:
            steer_dir = 1.0

        # Apply steering
        if steer_dir != 0:
            self._vehicle.steer(steer_dir, dt)       # POLYMORPHISM

        # Handbrake (space) — rapid deceleration
        if held_keys["space"]:
            if self._vehicle.current_speed > 0:
                self._vehicle.current_speed = max(
                    0, self._vehicle.current_speed - 20 * dt
                )
            elif self._vehicle.current_speed < 0:
                self._vehicle.current_speed = min(
                    0, self._vehicle.current_speed + 20 * dt
                )

        # Natural friction when not pressing gas or brake
        if not is_accelerating and not is_braking:
            self._vehicle.apply_friction(dt)         # INHERITANCE: shared method

        # ── Physics update ────────────────────────────────────────────
        self._vehicle.update_physics(dt)             # POLYMORPHISM

        # ── Collision detection ───────────────────────────────────────
        vehicle_pos = self._vehicle.position
        vehicle_radius = max(self._vehicle.width, self._vehicle.length) / 2.0

        for obs in self._level_manager.active_obstacles:
            if obs.check_collision(vehicle_pos, vehicle_radius):
                if self._collision_cooldown <= 0:
                    # Penalise score
                    self._score_manager.add_collision()
                    self._vehicle.take_damage(5)      # INHERITANCE: shared method
                    self._hud.update_collisions(self._score_manager.collision_count)
                    self._collision_cooldown = 0.5    # Half-second grace period

                # Push vehicle out of obstacle
                push = obs.get_push_direction(vehicle_pos)
                self._vehicle.position = Vec3(
                    vehicle_pos.x + push.x * 0.3,
                    0,
                    vehicle_pos.z + push.z * 0.3,
                )
                # Reduce speed on impact
                self._vehicle.current_speed *= 0.3

        # ── Boundary clamping ─────────────────────────────────────────
        pos = self._vehicle.position
        clamped = False
        if abs(pos.x) > 36:
            pos = Vec3(max(-36, min(36, pos.x)), pos.y, pos.z)
            clamped = True
        if abs(pos.z) > 36:
            pos = Vec3(pos.x, pos.y, max(-36, min(36, pos.z)))
            clamped = True
        if clamped:
            self._vehicle.position = pos
            self._vehicle.current_speed *= 0.5       # Slow on boundary hit

        # ── Parking detection ─────────────────────────────────────────
        all_parked = True
        vehicle_pos = self._vehicle.position
        vehicle_rot = self._vehicle.rotation_y

        for spot in self._level_manager.active_spots:
            parked = spot.is_vehicle_parked(vehicle_pos, vehicle_rot)
            spot.set_highlight(not parked and self._is_near_spot(vehicle_pos, spot))
            if not parked:
                all_parked = False

        if all_parked and abs(self._vehicle.current_speed) < 0.5:
            self._park_timer += dt
            self._hud.show_message("Hold still...", color.yellow)

            if self._park_timer >= self._park_threshold:
                # Successfully parked!
                self._complete_level()
                return
        else:
            self._park_timer = 0.0
            self._hud.clear_message()

        # ── Timer check ───────────────────────────────────────────────
        if self._score_manager.is_time_up:
            self._time_up()
            return

        # ── Camera update ─────────────────────────────────────────────
        self._camera_controller.update(
            self._vehicle.position,
            self._vehicle.rotation_y,
            dt,
        )

        # ── HUD update ───────────────────────────────────────────────
        self._hud.update_speed(self._vehicle.current_speed)
        self._hud.update_timer(self._score_manager.remaining_time)
        self._hud.update_score(self._score_manager.total_score)

    # ------------------------------------------------------------------
    # Helper: proximity check for spot highlighting
    # ------------------------------------------------------------------
    def _is_near_spot(self, vehicle_pos: Vec3, spot) -> bool:
        """Return True if the vehicle is within highlighting range of a spot."""
        dx = vehicle_pos.x - spot.position.x
        dz = vehicle_pos.z - spot.position.z
        return math.sqrt(dx * dx + dz * dz) < 5.0

    # ------------------------------------------------------------------
    # Level completion
    # ------------------------------------------------------------------
    def _complete_level(self) -> None:
        """Handle successful parking — show results screen."""
        # Calculate accuracy for each spot and add to score
        vehicle_pos = self._vehicle.position
        vehicle_rot = self._vehicle.rotation_y

        for spot in self._level_manager.active_spots:
            accuracy = spot.calculate_accuracy(vehicle_pos, vehicle_rot)
            self._score_manager.add_parking_score(accuracy)

        # Finalise score
        results = self._score_manager.finalize_level()

        # Determine if this is the last level
        is_last = (
            self._level_manager.current_level_index + 1
            >= self._level_manager.total_levels
        )

        # Show level-complete overlay
        self._hud.hide()
        self._menu.show_level_complete(results, is_last)
        self._state = STATE_LEVEL_COMPLETE

    def _time_up(self) -> None:
        """Handle time expiry — show game-over screen."""
        self._score_manager.stop_timer()
        self._hud.hide()
        self._menu.show_game_over(self._score_manager.total_score)
        self._state = STATE_GAME_OVER

    # ------------------------------------------------------------------
    # Key input handler (called by Ursina on key press)
    # ------------------------------------------------------------------
    def input(self, key: str) -> None:
        """Handle discrete key-press events (not held keys)."""
        # Pause / resume toggle
        if key == "escape":
            if self._state == STATE_PLAYING:
                self._state = STATE_PAUSED
                self._hud.hide()
                self._menu.show_pause_menu()
            elif self._state == STATE_PAUSED:
                self._resume_game()

        # Restart level
        if key == "r" and self._state == STATE_PLAYING:
            self._restart_level()

        # Switch vehicle
        if key == "v" and self._state == STATE_PLAYING:
            self._switch_vehicle()


# ==============================================================================
# Application entry point
# ==============================================================================
def main() -> None:
    """Create the Ursina app, instantiate the game, and run."""
    # Create the Ursina application
    app = Ursina(
        title="3D Car Parking Game",
        borderless=False,
        fullscreen=False,
        development_mode=False,                      # Suppress dev overlay
        size=(1280, 720),                            # Default window size
    )

    # Instantiate our game controller
    game = ParkingGame()

    # Run setup (scene, menus, HUD)
    game.setup()

    # Register per-frame and input callbacks with Ursina
    # Ursina looks for module-level `update` and `input` functions
    import __main__
    __main__.update = game.update
    __main__.input = game.input

    # Start the game loop
    app.run()


# Guard: only run when executed directly, not when imported
if __name__ == "__main__":
    main()
