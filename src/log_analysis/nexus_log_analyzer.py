"""
    Log File Analyzer for Game Development

    This script automates the process of analyzing a specified game directory fils. It does this by walking through each fild and examins every file determining if it has the .log extension. If it does, it will then parse the contents of the file searching for a predefined exception in the form of an error or warning. After identidying all the thrown exceptions in a log, it writes  the exception  to a table and displays the table to the console. The script also keeps track of the total number of logs processed, the number of errors and warnings found, and the number of clean logs that did not contain any exceptions.

    Modules:
    - os, re, json: Standard libraries for file handling, regular expressions, and JSON parsing.
    - rich: Library used to create enhanced console output with tables, progress bars, and styled text.
    - time: Used to track script execution time.
    - Constants: Configurations for log parsing (e.g., exception keywords, patterns).

    Usage:
        python <script_name>.py

    Attributes:
        CONFIG_FILE_PATH (str): Path to the configuration file storing the game directory.
        EXCEPTION_KEYWORDS (set): Set of keywords for identifying exceptions in logs.
        TIMESTAMP_PATTERN (Pattern): Regex pattern to identify timestamp entries in logs.
        EXCEPTION_PATTERN (Pattern): Compiled regex to match exception keywords.
        WARNING_KEYWORDS (set): Set of keywords specific to warnings.
"""

import os
import re
import json
from rich.table import Table
from time import perf_counter
from rich import print as rprint
from rich.console import Console
from rich.padding import Padding
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn

CONFIG_FILE_PATH = "config.json"
EXCEPTION_KEYWORDS = {
    "WARN",
    "warning",
    "error",
    "errors",
    "failed",
    "skipped",
    "nil value",
    "null value",
    "stack trace",
    "non-existent",
    "doesn't exist",
    "does not exist",
    "stack traceback:",
    "attempt to index",
    "attempted to index",
    "cannot be determined",
}

console = Console()
TIMESTAMP_PATTERN = re.compile(r"^\[\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}")
EXCEPTION_PATTERN = re.compile(
    r"\b(?:{})\b".format(
        "|".join(re.escape(keyword) for keyword in EXCEPTION_KEYWORDS)
    ),
    re.IGNORECASE,
)
WARNING_KEYWORDS = {"warn", "warning"}


def load_game_directory():
    """
    Loads the game directory path from the configuration file.

    Returns:
        str | None: Path to the game directory if loaded successfully, None otherwise.
    """
    try:
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config = json.load(config_file)
            is_game_directory = config.get("game_directory")

            if not is_game_directory or not os.path.exists(is_game_directory):
                print(
                    "Game directory not found in configuration. Setting up configuration..."
                )
                return create_config(config)

            return is_game_directory

    except (FileNotFoundError, json.JSONDecodeError):
        print("Configuration file missing or unreadable. Setting up configuration...")
        return create_config({})


def create_config(config):
    """
    Prompts the user to enter the game directory path and saves it to the configuration file.

    Args:
        config (dict): Dictionary to store configuration details.

    Returns:
        str | None: Path to the game directory if correctly configured, None otherwise.
    """
    is_game_directory_path = config.get("game_directory")
    if not is_game_directory_path or not os.path.exists(is_game_directory_path):
        is_game_directory_path = input(
            "Enter the full path to the game directory: "
        ).strip()
        if os.path.exists(is_game_directory_path):
            config["game_directory"] = is_game_directory_path
            with open(CONFIG_FILE_PATH, "w") as config_file:
                json.dump(config, config_file, indent=4)
            print(f"Game directory path saved to {CONFIG_FILE_PATH}.")
        else:
            print(
                "The provided game directory path does not exist. Please restart and enter a valid path."
            )
            return None

    return is_game_directory_path


def evaluate_log_entry(log_lines, errors, warnings, log_path):
    """
    Evaluates each log entry for potential errors or warnings.

    Args:
        log_lines (list[str]): List of log lines to analyze.
        errors (list[tuple]): List to store identified errors.
        warnings (list[tuple]): List to store identified warnings.
        log_path (str): Path of the log file being analyzed.
    """
    log_content = "".join(log_lines).strip().replace("|", r"\|")
    if any(keyword in log_content for keyword in WARNING_KEYWORDS):
        warnings.append((log_path, log_content))
    elif EXCEPTION_PATTERN.search(log_content):
        errors.append((log_path, log_content))


def parse_log_entries(log_path):
    """
    Parses log entries and categorizes them as errors or warnings.

    Args:
        log_path (str): Path to the log file.

    Returns:
        tuple[list[tuple], list[tuple]]: Lists of errors and warnings identified in the log file.
    """
    errors, warnings, log_lines = [], [], []
    with open(log_path, "r", encoding="utf-8") as each_log_file:
        for each_line in each_log_file:
            if TIMESTAMP_PATTERN.match(each_line):
                if log_lines:
                    evaluate_log_entry(log_lines, errors, warnings, log_path)
                    log_lines.clear()
            log_lines.append(each_line)
        if log_lines:
            evaluate_log_entry(log_lines, errors, warnings, log_path)
    return errors, warnings


def parse_redscript_log(log_path):
    """
    Parses the 'redscript' log for warnings based on custom format.

    Args:
        log_path (str): Path to the redscript log file.

    Returns:
        list[tuple]: List of warnings in the redscript log file.
    """
    warnings, warning_lines = [], []
    parsing_warning = False
    with open(log_path, "r", encoding="utf-8") as each_file:
        for each_line in each_file:
            if each_line.startswith("[WARN"):
                if warning_lines:
                    warnings.append((log_path, "".join(warning_lines).strip()))
                    warning_lines.clear()
                parsing_warning = True
                warning_lines.append(each_line)
            elif each_line.startswith("[INFO"):
                continue
            elif parsing_warning:
                warning_lines.append(each_line)
                if each_line.startswith("^^^") or not each_line.strip():
                    warnings.append((log_path, "".join(warning_lines).strip()))
                    warning_lines.clear()
                    parsing_warning = False
    if warning_lines:
        warnings.append((log_path, "".join(warning_lines).strip()))
    return warnings


def display_summary_table(total_logs, error_count, warning_count, clean_log_count):
    """
    Displays a summary table of log processing results.

    Args:
        total_logs (int): Total number of logs processed.
        error_count (int): Number of error logs found.
        warning_count (int): Number of warning logs found.
        clean_log_count (int): Number of clean logs found.
    """
    summary_table = Table(title="\nLog Processing Summary")
    summary_table.add_column("\nTotal Logs Processed", justify="center")
    summary_table.add_column("Clean Logs", justify="center")
    summary_table.add_column("Warnings Found", justify="center")
    summary_table.add_column("Errors Found", justify="center")
    summary_table.add_row(
        str(total_logs),
        f"[green]✅ {clean_log_count}[/green]",
        f"[yellow]🟡 {warning_count}[/yellow]",
        f"[red]🔴 {error_count}[/red]",
    )
    console.print(Padding(summary_table, (1, 10, 1, 10)))


def display_log_breakdown(header, icon, logs, category_label):
    """
    Displays a breakdown table for errors or warnings with specific log details.

    Args:
        header (str): Header title for the breakdown.
        icon (str): Icon representing the category.
        logs (list[tuple]): List of logs with content and path.
        category_label (str): Label for the category.
    """
    if not logs:
        return
    breakdown_table = Table(title=f"{header} Breakdown", show_lines=True)
    breakdown_table.add_column(f"{category_label}", style="bold", justify="left")
    breakdown_table.add_column("Location", justify="left")
    for each_log_path, each_log_content in logs:
        breakdown_table.add_row(f"{icon} {each_log_content}", each_log_path)
    console.print(Padding(breakdown_table, (1, 10, 1, 10)))


def process_logs(log_file_paths):
    """
    Processes each log file, categorizing entries and displaying progress.

    Args:
        log_file_paths (list[str]): List of log file paths to process.

    Returns:
        tuple: Summary statistics and categorized log entries.
    """
    total_logs_processed = 0
    time_elapsed = perf_counter()
    total_exceptions, total_warnings, total_cleaned = 0, 0, 0
    error_logs, warning_logs, clean_logs, missing_logs = [], [], [], []

    with Progress(
        TextColumn("[green]Logs Processed..."),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("", total=len(log_file_paths))

        for each_log_path in log_file_paths:
            if not os.path.exists(each_log_path):
                missing_logs.append(each_log_path)
                progress.advance(task)
                continue

            total_logs_processed += 1
            log_name = os.path.basename(each_log_path)

            if log_name == "redscript_rCURRENT.log":
                log_warnings = parse_redscript_log(each_log_path)
                log_errors = []
            else:
                log_errors, log_warnings = parse_log_entries(each_log_path)

            if log_errors:
                total_exceptions += len(log_errors)
                error_logs.extend(log_errors)
            if log_warnings:
                total_warnings += len(log_warnings)
                warning_logs.extend(log_warnings)
            if not log_errors and not log_warnings:
                total_cleaned += 1
                clean_logs.append((log_name, each_log_path))

            progress.advance(task)

        elapsed_time = perf_counter() - time_elapsed

        progress.update(
            task,
            description="[green]Logs Processed...[/green]",
            completed=len(log_file_paths),
        )

    console.print(f"[cyan]Time Elapsed: {elapsed_time:.2f} seconds[/cyan]")

    return (
        total_exceptions,
        total_warnings,
        total_cleaned,
        error_logs,
        warning_logs,
        clean_logs,
        missing_logs,
        total_logs_processed,
    )


def scan_directory_for_logs(directory_path):
    """
    Scans a directory for log files, processes each, and displays results.

    Args:
        directory_path (str): Directory path to scan for log files.
    """
    log_file_paths = []
    REDSCRIPT_LOG_PATH = r"G:\Steam Library\steamapps\common\Cyberpunk 2077\r6\logs\redscript_rCURRENT.log"
    for each_root, _, each_file in os.walk(directory_path):
        log_paths = [
            os.path.join(each_root, each_log)
            for each_log in each_file
            if each_log.endswith(".log")
        ]
        if (
            each_root == os.path.dirname(REDSCRIPT_LOG_PATH)
            and os.path.basename(REDSCRIPT_LOG_PATH) in each_file
        ):
            log_file_paths.append(REDSCRIPT_LOG_PATH)
        else:
            log_file_paths.extend(log_paths)

    (
        error_count,
        warning_count,
        clean_log_count,
        error_logs,
        warning_logs,
        clean_logs,
        missing_logs,
        logs_processed,
    ) = process_logs(log_file_paths)
    display_summary_table(logs_processed, error_count, warning_count, clean_log_count)
    display_log_breakdown("Errors", "🔴", error_logs, "Error Logs")
    display_log_breakdown("Warnings", "🟡", warning_logs, "Warning Logs")

    if clean_logs:
        clean_logs_table = Table(title="Clean Logs Breakdown", show_lines=True)
        clean_logs_table.add_column("Log Name", justify="left")
        clean_logs_table.add_column("Location", justify="left")
        for each_log_name, each_log_path in clean_logs:
            clean_logs_table.add_row(f"✅ {each_log_name}", each_log_path)
        console.print(Padding(clean_logs_table, (1, 10, 1, 10)))

    if missing_logs:
        missing_logs_table = Table(title="Logs Not Found", show_lines=True)
        missing_logs_table.add_column("Missing Log File Path", justify="left")
        for each_missing_log_path in missing_logs:
            missing_logs_table.add_row(f"{each_missing_log_path}")
        console.print(Padding(missing_logs_table, (1, 10, 1, 10)))


if __name__ == "__main__":
    GAME_DIRECTORY_PATH = load_game_directory()
    scan_directory_for_logs(GAME_DIRECTORY_PATH)
