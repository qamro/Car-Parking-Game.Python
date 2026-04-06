# ==============================================================================
# ui/__init__.py
# ==============================================================================
# Package initializer for the UI module.
# Provides the heads-up display and menu system for the game.
# ==============================================================================

from ui.hud import HUD      # In-game overlay
from ui.menu import Menu     # Main / pause menu

__all__ = ["HUD", "Menu"]
