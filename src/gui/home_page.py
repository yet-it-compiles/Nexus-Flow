"""
This module initializes the main window for the Modding Tool UI, sets up the sidebar navigation, and displays the home page and buttons for the other pages.
"""

import customtkinter as ctk
from log_analyzer_page import show_frame_2
from gui_styles import initialize_main_window, FONT_HEADER, FONT_SUBHEADER

root = initialize_main_window()


# Function to show the Home page
def show_home():
    """
    Displays the home page content on the content_frame.

    This function clears the content_frame and sets up the home page layout with a header and welcome
    message. It uses CTkLabel widgets for displaying the text.
    """
    header_label = ctk.CTkLabel(
        content_frame, text="Modding Tool - Home", font=FONT_HEADER
    )
    header_label.grid(row=0, column=0, padx=10, pady=30, sticky="n")

    home_label = ctk.CTkLabel(
        content_frame, text="Welcome to the Modding Tool", font=FONT_SUBHEADER
    )
    home_label.grid(row=1, column=0, padx=10, pady=10)


sidebar_frame = ctk.CTkFrame(root, width=140, corner_radius=0)
sidebar_frame.grid(row=0, column=0, sticky="ns")

home_button = ctk.CTkButton(sidebar_frame, text="Home", command=show_home)
home_button.grid(row=0, column=0, padx=10, pady=20, sticky="ew")

frame2_button = ctk.CTkButton(
    sidebar_frame, text="Log Analysis", command=lambda: show_frame_2(content_frame)
)
frame2_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

frame3_button = ctk.CTkButton(sidebar_frame, text="Settings")
frame3_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

sidebar_expanded = True


def toggle_sidebar():
    """
    Toggles the sidebar visibility and updates the toggle button's label.

    This function toggles the visibility of the sidebar by removing or restoring the grid configuration. It also updates the toggle button's label based on the current state of the sidebar.
    """
    global sidebar_expanded

    if sidebar_expanded:
        sidebar_frame.grid_forget()
        toggle_button.configure(text="➡️")
    else:
        sidebar_frame.grid(row=0, column=0, sticky="ns")
        toggle_button.configure(text="⬅️")
    sidebar_expanded = not sidebar_expanded


toggle_button = ctk.CTkButton(root, text="↔️", command=toggle_sidebar, width=30)
toggle_button.grid(row=0, column=0, sticky="ne", padx=5, pady=5)

content_frame = ctk.CTkFrame(root)
content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

# Ensure the grid layout is responsive
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Display the Home page on app start
show_home()

# Start the application
root.mainloop()
