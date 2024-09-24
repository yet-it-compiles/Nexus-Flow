"""
This module provides the initialization and styling settings for the Modding Tool's graphical user interface (GUI). It configures the appearance, theme, and font styles, ensuring consistency across the application.
"""

import customtkinter as ctk
from typing import Optional

# Set default appearance mode and theme
LIGHT_MODE = "light"
DEFAULT_MODE = "dark"
DEFAULT_THEME = "blue"
ctk.set_appearance_mode(DEFAULT_MODE)
ctk.set_default_color_theme(DEFAULT_THEME)


# Defines the windows dimensions and font styles
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
FONT_HEADER = ("Arial", 24)
FONT_SUBHEADER = ("Arial", 16)
FONT_STATUS = ("Arial", 12)


def set_appearance(theme: str = DEFAULT_THEME, mode: str = DEFAULT_MODE) -> None:
    """
    Sets the application's appearance mode and theme.

    Args:
        theme (str): The color theme to apply (default is 'blue').
        mode (str): The appearance mode ('dark' or 'light', default is 'dark').

    Returns:
        None
    """
    ctk.set_appearance_mode(mode)
    ctk.set_default_color_theme(theme)


def create_main_window(
    width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT
) -> Optional[ctk.CTk]:
    """
    Creates and initializes the main window for the Modding Auding Tools GUI with the specified dimensions.

    Args:
        width (int): The width of the application window (default is 900).
        height (int): The height of the application window (default is 700).

    Returns:
        Optional[ctk.CTk]: The initialized CTk root window instance or None if initialization fails.
    """
    try:
        main_window = ctk.CTk()
        main_window.geometry(f"{width}x{height}")
        main_window.title("Log Analyzer - Modding Tool")
        return main_window
    except Exception as e:
        print(f"Error initializing the main window: {e}")
        return None


# Apply the apps appearance settings
set_appearance()
