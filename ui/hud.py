# ==============================================================================
# ui/hud.py
# ==============================================================================
# Heads-Up Display — renders real-time game information on screen (speed,
# timer, score, level name, collision count).
#
# ENCAPSULATION: All Ursina Text entities are private; the game loop calls
# update_*() methods to push new data without knowing how rendering works.
# ==============================================================================

from ursina import Text, color, destroy, camera     # Ursina UI primitives


class HUD:
    """In-game overlay showing speed, timer, score, and status.

    ENCAPSULATION — rendering internals (Text entities, formatting) are private;
    the public API is a set of update_*() methods.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(self) -> None:
        # ENCAPSULATION: all UI entities are private
        self._speed_text: Text | None = None
        self._timer_text: Text | None = None
        self._score_text: Text | None = None
        self._level_text: Text | None = None
        self._collision_text: Text | None = None
        self._hint_text: Text | None = None
        self._message_text: Text | None = None      # Temporary centre-screen message
        self._is_visible: bool = False

    # ------------------------------------------------------------------
    # Properties (ENCAPSULATION)
    # ------------------------------------------------------------------
    @property
    def is_visible(self) -> bool:
        """Return whether the HUD is currently shown."""
        return self._is_visible

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def create(self) -> None:
        """Instantiate all HUD text elements."""
        # Speed indicator — bottom-left
        self._speed_text = Text(
            text="Speed: 0",
            position=(-0.85, -0.42),
            scale=1.2,
            color=color.white,
        )

        # Timer — top-centre
        self._timer_text = Text(
            text="Time: 60s",
            position=(-0.08, 0.47),
            scale=1.5,
            color=color.white,
        )

        # Score — top-right
        self._score_text = Text(
            text="Score: 0",
            position=(0.55, 0.47),
            scale=1.2,
            color=color.yellow,
        )

        # Level name — top-left
        self._level_text = Text(
            text="Level 1",
            position=(-0.85, 0.47),
            scale=1.3,
            color=color.cyan,
        )

        # Collision counter — bottom-right
        self._collision_text = Text(
            text="Hits: 0",
            position=(0.6, -0.42),
            scale=1.1,
            color=color.rgb(255, 100, 100),
        )

        # Control hints — bottom-centre
        self._hint_text = Text(
            text="WASD/Arrows: Drive | SPACE: Handbrake | R: Reset | V: Switch Vehicle",
            position=(-0.55, -0.47),
            scale=0.8,
            color=color.rgb(200, 200, 200),
        )

        # Centre message (hidden by default)
        self._message_text = Text(
            text="",
            position=(-0.15, 0.1),
            scale=2.5,
            color=color.white,
        )

        self._is_visible = True

    def destroy(self) -> None:
        """Remove all HUD elements from the screen."""
        for attr in (
            "_speed_text", "_timer_text", "_score_text",
            "_level_text", "_collision_text", "_hint_text",
            "_message_text",
        ):
            entity = getattr(self, attr, None)
            if entity:
                destroy(entity)
                setattr(self, attr, None)
        self._is_visible = False

    # ------------------------------------------------------------------
    # Update methods (ENCAPSULATION — callers push data, HUD handles display)
    # ------------------------------------------------------------------
    def update_speed(self, speed: float) -> None:
        """Update the speed readout."""
        if self._speed_text:
            display_speed = abs(speed)
            kmh = int(display_speed * 10)            # Arbitrary scale for "km/h" feel
            self._speed_text.text = f"Speed: {kmh} km/h"

    def update_timer(self, remaining: float) -> None:
        """Update the countdown timer."""
        if self._timer_text:
            mins = int(remaining) // 60
            secs = int(remaining) % 60
            self._timer_text.text = f"Time: {mins}:{secs:02d}"

            # Flash red when time is running low
            if remaining < 10:
                self._timer_text.color = color.red
            elif remaining < 20:
                self._timer_text.color = color.yellow
            else:
                self._timer_text.color = color.white

    def update_score(self, score: float) -> None:
        """Update the score display."""
        if self._score_text:
            self._score_text.text = f"Score: {int(score)}"

    def update_level(self, level_num: int, level_name: str) -> None:
        """Update the level indicator."""
        if self._level_text:
            self._level_text.text = f"Lv.{level_num}: {level_name}"

    def update_collisions(self, count: int) -> None:
        """Update the collision counter."""
        if self._collision_text:
            self._collision_text.text = f"Hits: {count}"

    def show_message(self, text: str, msg_color=None) -> None:
        """Show a temporary centre-screen message (e.g. 'Level Complete!')."""
        if self._message_text:
            self._message_text.text = text
            self._message_text.color = msg_color if msg_color else color.white

    def clear_message(self) -> None:
        """Hide the centre-screen message."""
        if self._message_text:
            self._message_text.text = ""

    def hide(self) -> None:
        """Make all HUD elements invisible."""
        for attr in (
            "_speed_text", "_timer_text", "_score_text",
            "_level_text", "_collision_text", "_hint_text",
            "_message_text",
        ):
            entity = getattr(self, attr, None)
            if entity:
                entity.visible = False
        self._is_visible = False

    def show(self) -> None:
        """Make all HUD elements visible again."""
        for attr in (
            "_speed_text", "_timer_text", "_score_text",
            "_level_text", "_collision_text", "_hint_text",
            "_message_text",
        ):
            entity = getattr(self, attr, None)
            if entity:
                entity.visible = True
        self._is_visible = True
