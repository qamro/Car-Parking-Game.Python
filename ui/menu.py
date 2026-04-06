# ==============================================================================
# ui/menu.py
# ==============================================================================
# Main menu, pause menu, level-complete overlay, and game-over screen.
#
# ENCAPSULATION: All button and text entities are private; the game loop
# interacts through show_*() / hide_*() methods and callback registration.
# ==============================================================================

from ursina import (                                # Ursina UI primitives
    Text, Button, Entity, color, destroy,
    application, camera,
)


class Menu:
    """Manages all non-gameplay UI screens.

    ENCAPSULATION — UI layout and widget references are hidden; the game
    registers callbacks and calls show/hide methods.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(self) -> None:
        # ENCAPSULATION: private widget references
        self._main_menu_entities: list = []        # Widgets on the title screen
        self._pause_entities: list = []            # Widgets on the pause overlay
        self._complete_entities: list = []         # Widgets on the level-complete screen
        self._gameover_entities: list = []         # Widgets on the game-over screen

        # Callback functions — set by the game loop
        self._on_start: callable = None
        self._on_resume: callable = None
        self._on_restart: callable = None
        self._on_next_level: callable = None
        self._on_quit: callable = None
        self._on_select_vehicle: callable = None

    # ------------------------------------------------------------------
    # Callback registration (ENCAPSULATION — the menu doesn't know game logic)
    # ------------------------------------------------------------------
    def set_callbacks(
        self,
        on_start=None,
        on_resume=None,
        on_restart=None,
        on_next_level=None,
        on_quit=None,
        on_select_vehicle=None,
    ) -> None:
        """Register callback functions for menu actions."""
        self._on_start = on_start
        self._on_resume = on_resume
        self._on_restart = on_restart
        self._on_next_level = on_next_level
        self._on_quit = on_quit
        self._on_select_vehicle = on_select_vehicle

    # ------------------------------------------------------------------
    # Main Menu
    # ------------------------------------------------------------------
    def show_main_menu(self) -> None:
        """Display the title screen with Start and Quit buttons."""
        self.hide_main_menu()                       # Clear any existing widgets

        # Background overlay
        bg = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(0, 0, 0, 200),
            scale=(2, 2),
            z=1,
        )
        self._main_menu_entities.append(bg)

        # Game title
        title = Text(
            text="3D CAR PARKING",
            position=(-0.28, 0.35),
            scale=3.5,
            color=color.cyan,
        )
        self._main_menu_entities.append(title)

        # Subtitle
        subtitle = Text(
            text="Master the art of parking!",
            position=(-0.2, 0.25),
            scale=1.5,
            color=color.light_gray,
        )
        self._main_menu_entities.append(subtitle)

        # Start button
        start_btn = Button(
            text="START GAME",
            color=color.rgb(0, 150, 0),
            highlight_color=color.rgb(0, 200, 0),
            scale=(0.3, 0.07),
            position=(0, 0.05),
        )
        start_btn.on_click = self._handle_start
        self._main_menu_entities.append(start_btn)

        # Vehicle select info
        veh_text = Text(
            text="Press V during gameplay to switch vehicles",
            position=(-0.25, -0.08),
            scale=1,
            color=color.rgb(180, 180, 180),
        )
        self._main_menu_entities.append(veh_text)

        # Controls info
        controls = Text(
            text="Controls: WASD / Arrow Keys to drive\n"
            "SPACE = Handbrake  |  R = Restart Level  |  ESC = Pause",
            position=(-0.35, -0.2),
            scale=0.9,
            color=color.rgb(160, 160, 160),
        )
        self._main_menu_entities.append(controls)

        # Quit button
        quit_btn = Button(
            text="QUIT",
            color=color.rgb(150, 0, 0),
            highlight_color=color.rgb(200, 0, 0),
            scale=(0.3, 0.07),
            position=(0, -0.35),
        )
        quit_btn.on_click = self._handle_quit
        self._main_menu_entities.append(quit_btn)

    def hide_main_menu(self) -> None:
        """Remove all main-menu widgets."""
        for e in self._main_menu_entities:
            destroy(e)
        self._main_menu_entities.clear()

    # ------------------------------------------------------------------
    # Pause Menu
    # ------------------------------------------------------------------
    def show_pause_menu(self) -> None:
        """Display the pause overlay."""
        self.hide_pause_menu()

        bg = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(0, 0, 0, 150),
            scale=(2, 2),
            z=1,
        )
        self._pause_entities.append(bg)

        title = Text(
            text="PAUSED",
            position=(-0.1, 0.2),
            scale=3,
            color=color.white,
        )
        self._pause_entities.append(title)

        resume_btn = Button(
            text="RESUME",
            color=color.rgb(0, 120, 0),
            highlight_color=color.rgb(0, 180, 0),
            scale=(0.3, 0.07),
            position=(0, 0),
        )
        resume_btn.on_click = self._handle_resume
        self._pause_entities.append(resume_btn)

        restart_btn = Button(
            text="RESTART LEVEL",
            color=color.rgb(180, 120, 0),
            highlight_color=color.rgb(220, 150, 0),
            scale=(0.3, 0.07),
            position=(0, -0.12),
        )
        restart_btn.on_click = self._handle_restart
        self._pause_entities.append(restart_btn)

        quit_btn = Button(
            text="QUIT TO MENU",
            color=color.rgb(150, 0, 0),
            highlight_color=color.rgb(200, 0, 0),
            scale=(0.3, 0.07),
            position=(0, -0.24),
        )
        quit_btn.on_click = self._handle_quit
        self._pause_entities.append(quit_btn)

    def hide_pause_menu(self) -> None:
        """Remove all pause-menu widgets."""
        for e in self._pause_entities:
            destroy(e)
        self._pause_entities.clear()

    # ------------------------------------------------------------------
    # Level Complete Screen
    # ------------------------------------------------------------------
    def show_level_complete(self, results: dict, is_last_level: bool = False) -> None:
        """Display the level-complete summary with score and stars."""
        self.hide_level_complete()

        bg = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(0, 0, 0, 180),
            scale=(2, 2),
            z=1,
        )
        self._complete_entities.append(bg)

        # Title
        title_text = "ALL LEVELS COMPLETE!" if is_last_level else "LEVEL COMPLETE!"
        title = Text(
            text=title_text,
            position=(-0.25, 0.3),
            scale=2.5,
            color=color.rgb(0, 255, 100),
        )
        self._complete_entities.append(title)

        # Stars
        stars = results.get("stars", 0)
        star_str = "\u2605" * stars + "\u2606" * (3 - stars)   # Filled + empty stars
        star_display = Text(
            text=star_str,
            position=(-0.08, 0.2),
            scale=3,
            color=color.yellow,
        )
        self._complete_entities.append(star_display)

        # Stats
        stats = (
            f'Score: {results.get("level_score", 0)}\n'
            f'Time Bonus: +{results.get("time_bonus", 0)}\n'
            f'Time: {results.get("elapsed_time", 0)}s\n'
            f'Collisions: {results.get("collisions", 0)}\n'
            f'Total Score: {results.get("total_score", 0)}'
        )
        stats_text = Text(
            text=stats,
            position=(-0.2, 0.08),
            scale=1.2,
            color=color.white,
        )
        self._complete_entities.append(stats_text)

        if not is_last_level:
            next_btn = Button(
                text="NEXT LEVEL",
                color=color.rgb(0, 150, 0),
                highlight_color=color.rgb(0, 200, 0),
                scale=(0.3, 0.07),
                position=(0, -0.2),
            )
            next_btn.on_click = self._handle_next_level
            self._complete_entities.append(next_btn)

        restart_btn = Button(
            text="RETRY LEVEL",
            color=color.rgb(180, 120, 0),
            highlight_color=color.rgb(220, 150, 0),
            scale=(0.3, 0.07),
            position=(0, -0.32),
        )
        restart_btn.on_click = self._handle_restart
        self._complete_entities.append(restart_btn)

        menu_btn = Button(
            text="MAIN MENU",
            color=color.rgb(100, 100, 100),
            highlight_color=color.rgb(150, 150, 150),
            scale=(0.3, 0.07),
            position=(0, -0.44),
        )
        menu_btn.on_click = self._handle_quit
        self._complete_entities.append(menu_btn)

    def hide_level_complete(self) -> None:
        """Remove level-complete widgets."""
        for e in self._complete_entities:
            destroy(e)
        self._complete_entities.clear()

    # ------------------------------------------------------------------
    # Game Over Screen
    # ------------------------------------------------------------------
    def show_game_over(self, total_score: float) -> None:
        """Display the game-over screen (time ran out)."""
        self.hide_game_over()

        bg = Entity(
            parent=camera.ui,
            model="quad",
            color=color.rgba(0, 0, 0, 200),
            scale=(2, 2),
            z=1,
        )
        self._gameover_entities.append(bg)

        title = Text(
            text="TIME'S UP!",
            position=(-0.15, 0.2),
            scale=3,
            color=color.red,
        )
        self._gameover_entities.append(title)

        score_text = Text(
            text=f"Total Score: {int(total_score)}",
            position=(-0.15, 0.05),
            scale=1.5,
            color=color.white,
        )
        self._gameover_entities.append(score_text)

        restart_btn = Button(
            text="RETRY LEVEL",
            color=color.rgb(180, 120, 0),
            highlight_color=color.rgb(220, 150, 0),
            scale=(0.3, 0.07),
            position=(0, -0.12),
        )
        restart_btn.on_click = self._handle_restart
        self._gameover_entities.append(restart_btn)

        menu_btn = Button(
            text="MAIN MENU",
            color=color.rgb(100, 100, 100),
            highlight_color=color.rgb(150, 150, 150),
            scale=(0.3, 0.07),
            position=(0, -0.24),
        )
        menu_btn.on_click = self._handle_quit
        self._gameover_entities.append(menu_btn)

    def hide_game_over(self) -> None:
        """Remove game-over widgets."""
        for e in self._gameover_entities:
            destroy(e)
        self._gameover_entities.clear()

    # ------------------------------------------------------------------
    # Hide all overlays
    # ------------------------------------------------------------------
    def hide_all(self) -> None:
        """Remove every menu overlay."""
        self.hide_main_menu()
        self.hide_pause_menu()
        self.hide_level_complete()
        self.hide_game_over()

    # ------------------------------------------------------------------
    # Internal handlers (forward to registered callbacks)
    # ------------------------------------------------------------------
    def _handle_start(self) -> None:
        if self._on_start:
            self._on_start()

    def _handle_resume(self) -> None:
        if self._on_resume:
            self._on_resume()

    def _handle_restart(self) -> None:
        if self._on_restart:
            self._on_restart()

    def _handle_next_level(self) -> None:
        if self._on_next_level:
            self._on_next_level()

    def _handle_quit(self) -> None:
        if self._on_quit:
            self._on_quit()
