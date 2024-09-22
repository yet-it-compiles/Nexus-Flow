"""
This module provides the initialization and styling settings for the Modding Tool's graphical user interface (GUI). It configures the appearance, theme, and font styles, ensuring consistency across the application.
"""

import customtkinter as ctk
from typing import Optional

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# Typography, and Apperance Constants
APP_WIDTH = 900
APP_HEIGHT = 700
FONT_HEADER = ("Arial", 24)
FONT_SUBHEADER = ("Arial", 16)
FONT_STATUS = ("Arial", 12)


def configure_appearance(theme: str = "blue", mode: str = "dark") -> None:
    """
    Configures the application's appearance mode and theme.

    Parameters:
        theme (str): The color theme to apply (default is 'blue').
        mode (str): The appearance mode ('dark' or 'light', default is 'dark').

    Returns:
        None
    """
    ctk.set_appearance_mode(mode)
    ctk.set_default_color_theme(theme)


def initialize_main_window(
    width: int = APP_WIDTH, height: int = APP_HEIGHT
) -> Optional[ctk.CTk]:
    """
    Initializes the main window for the Modding Tool GUI with the specified dimensions.

    Parameters:
        width (int): The width of the application window (default is 900).
        height (int): The height of the application window (default is 700).

    Returns:
        root (ctk.CTk): The initialized CTk root window instance.
    """
    try:
        root = ctk.CTk()
        root.geometry(f"{width}x{height}")
        root.title("Log Analyzer - Modding Tool")
        return root
    except Exception as e:
        print(f"Error initializing the main window: {e}")
        return None


# Apply default appearance settings
configure_appearance()
