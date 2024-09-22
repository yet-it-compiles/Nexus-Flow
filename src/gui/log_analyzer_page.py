"""
This module provides the functionality for displaying the log analysis page in the Modding Tool's GUI. It includes functions for analyzing logs, exporting logs, and updating the user interface with relevant feedback via a progress bar and status messages.
"""

import customtkinter as ctk
from tkinter import filedialog
from gui_styles import FONT_SUBHEADER


def clear_content_frame(content_frame):
    """
    @TODO

    Clears all widgets from the given content_frame.

    Args:
        content_frame (CTkFrame): The frame whose content will be cleared.

    This utility function removes all widgets currently within the content_frame to allow for the display of new content, ensuring that no old widgets are left on the screen.
    """
    for each_widget in content_frame.winfo_children():
        each_widget.destroy()


def show_frame_2(content_frame):
    """
    @TODO

    Displays the log analysis interface on the content_frame.

    Args:
        content_frame (CTkFrame): The frame where the log analysis interface will be displayed.

    This function clears the existing content from the content_frame and creates a tabbed interface for viewing log entries (Errors, Warnings, and Clean Logs). It also adds buttons for log analysis, export functionality, and clearing logs. Additionally, a progress bar and status bar are created to provide visual feedback on the log analysis process.
    """
    clear_content_frame(content_frame)

    tabview = ctk.CTkTabview(content_frame, width=600)
    tabview.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    tabview.add("Errors")
    tabview.add("Warnings")
    tabview.add("Clean Logs")

    errors_scroll_frame = ctk.CTkScrollableFrame(tabview.tab("Errors"))
    errors_scroll_frame.pack(fill="both", expand=True)

    warnings_scroll_frame = ctk.CTkScrollableFrame(tabview.tab("Warnings"))
    warnings_scroll_frame.pack(fill="both", expand=True)

    clean_logs_scroll_frame = ctk.CTkScrollableFrame(tabview.tab("Clean Logs"))
    clean_logs_scroll_frame.pack(fill="both", expand=True)

    error_label = ctk.CTkLabel(
        errors_scroll_frame, text="No Errors Found", font=FONT_SUBHEADER
    )
    error_label.pack(pady=20)

    warning_label = ctk.CTkLabel(
        warnings_scroll_frame, text="No Warnings Found", font=FONT_SUBHEADER
    )
    warning_label.pack(pady=20)

    clean_log_label = ctk.CTkLabel(
        clean_logs_scroll_frame, text="All Logs Clean", font=FONT_SUBHEADER
    )
    clean_log_label.pack(pady=20)

    analyze_button = ctk.CTkButton(
        content_frame, text="Analyze Logs", command=analyze_logs
    )
    analyze_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    export_logs_button = ctk.CTkButton(
        content_frame, text="Export Logs", command=export_logs
    )
    export_logs_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

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

    This placeholder function simulates the completion of a log analysis process by updating the progress bar to 100% and updating the status bar to indicate that the log analysis is complete.
    """
    update_status("Analyzing logs...")
    progress_bar.set(1.0)
    update_status("Log analysis complete!")


def export_logs():
    """
    @TODO

    Opens a file save dialog for exporting logs and updates the status bar upon completion.

    This function prompts the user with a filedialog to choose a location to save the exported logs. It then updates the status bar to indicate the success of the export operation.
    """
    export_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    if export_path:
        update_status(f"Logs exported to {export_path}")


def update_status(message):
    """
    @TODO

    Updates the status bar with the provided message.

    Args:
        message (str): The message to be displayed in the status bar.

    This function updates the text of the global status_bar widget with the given message to reflect
    the current state or action of the application.
    """
    status_bar.configure(text=message)
