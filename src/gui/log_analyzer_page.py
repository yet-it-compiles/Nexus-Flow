"""
This module provides the functionality for displaying the log analysis page in the Modding Tool's GUI. It includes functions for analyzing logs, exporting logs, and updating the user interface with relevant feedback via a progress bar and status messages.
"""

import customtkinter as ctk
from tkinter import filedialog
from gui_styles import FONT_SUBHEADER


def clear_frame_content(frame_to_clear):
    """
    @TODO

    Clears all widgets from the given content_frame.

    Args:
        content_frame (CTkFrame): The frame whose content will be cleared.

    This utility function removes all widgets currently within the content_frame to allow for the display of new content, ensuring that no old widgets are left on the screen.
    """
    for each_widget in frame_to_clear.winfo_children():
        each_widget.destroy()


def display_log_analysis_page(content_frame):
    """
    @TODO

    Displays the log analysis interface on the content_frame.

    Args:
        content_frame (CTkFrame): The frame where the log analysis interface will be displayed.

    This function clears the existing content from the content_frame and creates a tabbed interface for viewing log entries (Errors, Warnings, and Clean Logs). It also adds buttons for log analysis, export functionality, and clearing logs. Additionally, a progress bar and status bar are created to provide visual feedback on the log analysis process.
    """
    clear_frame_content(content_frame)

    """ Defines a tabbed view for the analysis categories """
    tab_view = ctk.CTkTabview(content_frame, width=600)
    tab_view.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    tab_view.add("Errors")
    tab_view.add("Warnings")
    tab_view.add("Clean Logs")

    log_error_frame = ctk.CTkScrollableFrame(tab_view.tab("Errors"))
    log_error_frame.pack(fill="both", expand=True)

    log_warning_frame = ctk.CTkScrollableFrame(tab_view.tab("Warnings"))
    log_warning_frame.pack(fill="both", expand=True)

    clean_logs_frame = ctk.CTkScrollableFrame(tab_view.tab("Clean Logs"))
    clean_logs_frame.pack(fill="both", expand=True)

    error_label = ctk.CTkLabel(
        log_error_frame, text="No Errors Found", font=FONT_SUBHEADER
    )
    error_label.pack(pady=20)

    warning_label = ctk.CTkLabel(
        log_warning_frame, text="No Warnings Found", font=FONT_SUBHEADER
    )
    warning_label.pack(pady=20)

    clean_log_label = ctk.CTkLabel(
        clean_logs_frame, text="All Logs Clean", font=FONT_SUBHEADER
    )
    clean_log_label.pack(pady=20)

    analyze_button = ctk.CTkButton(
        content_frame, text="Analyze Logs", command=analyze_logs
    )
    analyze_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    export_button = ctk.CTkButton(
        content_frame, text="Export Logs", command=export_logs
    )
    export_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

    clear_logs_button = ctk.CTkButton(content_frame, text="Clear Logs")
    clear_logs_button.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

    global progress_bar
    progress_bar = ctk.CTkProgressBar(content_frame, width=400)
    progress_bar.grid(row=7, column=0, padx=10, pady=20, sticky="ew")
    progress_bar.set(0.0)

    global status_bar
    status_bar = ctk.CTkLabel(
        content_frame, text="Ready", anchor="w", font=FONT_SUBHEADER
    )
    status_bar.grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=5)


def analyze_logs():
    """
    @TODO

    Simulates the log analysis process and updates the status bar and progress bar.

    Placeholder function simulating the completion of a log analysis process by updating the progress bar to 100% and updating the status bar to indicate that the log analysis is complete.
    """
    update_status_message("Analyzing logs...")
    progress_bar.set(1.0)
    update_status_message("Log analysis complete!")


def export_logs():
    """
    @TODO

    Opens file dialog for exporting and updates the status bar when completion.

    This function prompts the user with a filedialog to choose a location to save the exported logs. It then updates the status bar to indicate the success of the export operation.
    """
    is_export_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    if is_export_path:
        update_status_message(f"Logs exported to {is_export_path}")


def update_status_message(status_message):
    """
    @TODO

    Updates the status bar with the provided message.

    Args:
        status_message (str): The message to be displayed in the status bar.

    This function updates the text of the global status_bar widget with the given message to reflect the state of the application.
    """
    status_bar.configure(text=status_message)
