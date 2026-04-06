# ==============================================================================
# game/score_manager.py
# ==============================================================================
# Tracks the player's score, time, collision penalties, and star rating.
#
# ENCAPSULATION: All scoring internals are private; the game loop reads results
# through properties and calls start_timer / stop_timer / add_score.
# ==============================================================================

import time as _time                              # Wall-clock timer


class ScoreManager:
    """Calculates and stores the player's score for a level.

    ENCAPSULATION — internal counters are private; public interface is minimal.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(self) -> None:
        self._total_score: float = 0.0             # Cumulative score across levels
        self._level_score: float = 0.0             # Score for the current level
        self._collision_count: int = 0             # Collisions this level
        self._collision_penalty: float = 5.0       # Points deducted per collision
        self._time_bonus_max: float = 50.0         # Max bonus for fast completion
        self._start_time: float = 0.0              # Level start timestamp
        self._elapsed_time: float = 0.0            # Seconds elapsed this level
        self._is_timing: bool = False              # Whether the timer is running
        self._level_time_limit: float = 60.0       # Current level's time limit
        self._paused_elapsed: float = 0.0          # Accumulated time before pause

    # ------------------------------------------------------------------
    # Properties (ENCAPSULATION — controlled reads)
    # ------------------------------------------------------------------
    @property
    def total_score(self) -> float:
        """Return cumulative score across all levels."""
        return self._total_score

    @property
    def level_score(self) -> float:
        """Return score earned in the current level."""
        return self._level_score

    @property
    def collision_count(self) -> int:
        """Return number of collisions in this level."""
        return self._collision_count

    @property
    def elapsed_time(self) -> float:
        """Return total seconds elapsed (accounts for pauses)."""
        if self._is_timing:
            return self._paused_elapsed + (_time.time() - self._start_time)
        return self._elapsed_time

    @property
    def remaining_time(self) -> float:
        """Return seconds remaining before time runs out."""
        return max(0.0, self._level_time_limit - self.elapsed_time)

    @property
    def is_time_up(self) -> bool:
        """Return True if the level timer has expired."""
        return self.elapsed_time >= self._level_time_limit

    # ------------------------------------------------------------------
    # Timer controls
    # ------------------------------------------------------------------
    def start_timer(self, time_limit: float) -> None:
        """Begin the level timer with the given limit (seconds)."""
        self._start_time = _time.time()
        self._level_time_limit = time_limit
        self._is_timing = True
        self._paused_elapsed = 0.0                 # Reset accumulated pause time
        self._level_score = 0.0
        self._collision_count = 0

    def stop_timer(self) -> None:
        """Stop the level timer and record elapsed time."""
        if self._is_timing:
            self._elapsed_time = self._paused_elapsed + (_time.time() - self._start_time)
            self._is_timing = False

    def pause_timer(self) -> None:
        """Pause the timer — accumulates elapsed time so far and stops the clock.

        Called when the game enters the PAUSED state so the countdown does not
        continue while the pause menu is open.
        """
        if self._is_timing:
            self._paused_elapsed += _time.time() - self._start_time
            self._elapsed_time = self._paused_elapsed  # Keep elapsed_time in sync
            self._is_timing = False

    def resume_timer(self) -> None:
        """Resume the timer after a pause — resets the start time to now."""
        if not self._is_timing:
            self._start_time = _time.time()        # Restart the clock from now
            self._is_timing = True

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------
    def add_parking_score(self, accuracy: float) -> None:
        """Add parking accuracy points to the level score.

        *accuracy* is 0-100 from ParkingSpot.calculate_accuracy().
        """
        self._level_score += accuracy

    def add_collision(self) -> None:
        """Record a collision and apply a point penalty."""
        self._collision_count += 1
        self._level_score = max(0.0, self._level_score - self._collision_penalty)

    def calculate_time_bonus(self) -> float:
        """Return a bonus for finishing quickly.

        Full bonus if finished in under 50 % of the time limit; zero bonus at
        100 % of the time limit; linear interpolation in between.
        """
        if self._elapsed_time <= 0:
            return self._time_bonus_max

        ratio = self._elapsed_time / self._level_time_limit
        if ratio <= 0.5:
            return self._time_bonus_max            # Under half time = full bonus
        if ratio >= 1.0:
            return 0.0                              # Over time = no bonus

        # Linear interpolation between 50 % and 100 % of time limit
        return self._time_bonus_max * (1.0 - (ratio - 0.5) / 0.5)

    def finalize_level(self) -> dict:
        """Stop the timer, add time bonus, and return a summary dictionary."""
        self.stop_timer()

        time_bonus = self.calculate_time_bonus()
        self._level_score += time_bonus

        # Clamp level score to 0
        self._level_score = max(0.0, self._level_score)

        # Add to cumulative total
        self._total_score += self._level_score

        return {
            "level_score": round(self._level_score, 1),
            "time_bonus": round(time_bonus, 1),
            "collisions": self._collision_count,
            "elapsed_time": round(self._elapsed_time, 1),
            "stars": self.get_stars(),
            "total_score": round(self._total_score, 1),
        }

    def get_stars(self) -> int:
        """Return a 1-3 star rating based on level score.

        ★★★ = 80+ points, ★★ = 50-79, ★ = 1-49, 0 = 0 points.
        """
        if self._level_score >= 80:
            return 3
        if self._level_score >= 50:
            return 2
        if self._level_score > 0:
            return 1
        return 0

    def reset_level(self) -> None:
        """Reset level-specific counters (called before loading a new level)."""
        self._level_score = 0.0
        self._collision_count = 0
        self._elapsed_time = 0.0
        self._paused_elapsed = 0.0
        self._is_timing = False

    def reset_all(self) -> None:
        """Reset everything including cumulative total (for New Game)."""
        self.reset_level()
        self._total_score = 0.0
