"""
Log Analysis Script for Cyberpunk 2077

This script processes all the log files from the Cyberpunk 2077 game directory to classify errors, warnings, and clean logs within. It generates a Markdown report summarizing the findings, including details about specific error and warning occurrences in various log files.

Modules:
    - os: Provides functions for interacting with the operating system.
    - re: Offers support for regular expressions.
    - time: Used to simulate delays in processing.
    - rich.progress: Displays progress bars in the terminal.
    - rich: Used for colored and stylized terminal printing.

Functions:
    - process_log_entry: Processes individual log entries to classify errors and warnings.
    - classify_log_entries: Classifies log entries from standard logs.
    - classify_redscript_log_entries: Handles the specific log format of redscript_rCURRENT.log.
    - generate_summary_table: Generates a summary table in Markdown format.
    - generate_breakdown_table: Generates detailed breakdown tables for errors, warnings, and clean logs.
    - process_logs_with_progress: Processes a list of log files and reports errors, warnings, and clean logs.
    - process_log_files_in_directory: Orchestrates log file processing by scanning a directory for log files.
"""

import os
import re
import time
from rich.progress import Progress
from rich import print as rprint

# Keywords to look for in log files
IS_EXCEPTION_KEYWORDS = {
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

TIMESTAMP_REGEX = re.compile(r"^\[\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}")
EXCEPTION_REGEX = re.compile(
    r"\b(?:{})\b".format(
        "|".join(re.escape(each_key) for each_key in IS_EXCEPTION_KEYWORDS)
    ),
    re.IGNORECASE,
)
WARNING_KEYWORDS = {"warn", "warning"}


def process_log_entry(log_entries, error_list, warning_list, log_file_path):
    """
    Processes individual log entries by checking for errors or warnings based on predefined keywords.

    Args:
        log_entries (list): The log entries that make up a single log entry block.
        error_list (list): The list to which identified errors are appended.
        warning_list (list): The list to which identified warnings are appended.
        log_file_path (str): The file path of the current log file being processed.
    """
    every_read_log = "".join(log_entries).strip().replace("|", r"\|")

    if any(keyword in every_read_log for keyword in WARNING_KEYWORDS):
        warning_list.append((log_file_path, every_read_log))
    elif EXCEPTION_REGEX.search(every_read_log):
        error_list.append((log_file_path, every_read_log))


def classify_log_entries(log_file_path):
    """
    Classifies log entries into errors and warnings by scanning the log file.

    Args:
        log_file_path (str): The path to the log file being classified.

    Returns:
        tuple: Two lists containing errors and warnings respectively.
    """

    list_of_errors, list_of_warnings, list_of_log_files = [], [], []
    with open(log_file_path, "r", encoding="utf-8") as log_files:
        for each_log in log_files:
            if TIMESTAMP_REGEX.match(each_log):
                if list_of_log_files:
                    process_log_entry(
                        list_of_log_files,
                        list_of_errors,
                        list_of_warnings,
                        log_file_path,
                    )
                    list_of_log_files.clear()
            list_of_log_files.append(each_log)
        if list_of_log_files:
            process_log_entry(
                list_of_log_files, list_of_errors, list_of_warnings, log_file_path
            )
    return list_of_errors, list_of_warnings


def classify_redscript_log(log_file_path):
    """
    Classifies log entries from a standard log file, separating errors and warnings.

    Args:
        log_file_path (str): The path to the log file to be classified.

    Returns:
        tuple: Two lists containing errors and warnings respectively.
    """
    warnings = []
    current_warning = []
    is_warning = False

    with open(log_file_path, "r", encoding="utf-8") as file:
        for each_warning in file:
            if each_warning.startswith("[WARN"):
                if current_warning:
                    warnings.append(
                        (
                            log_file_path,
                            "".join(current_warning).strip(),
                        )
                    )
                    current_warning = []

                is_warning = True
                current_warning.append(each_warning)
            elif each_warning.startswith("[INFO"):
                continue
            elif is_warning:
                current_warning.append(each_warning)
                if each_warning.startswith("^^^") or not each_warning.strip():
                    warnings.append(
                        (
                            log_file_path,
                            "".join(current_warning).strip(),
                        )
                    )
                    current_warning = []
                    is_warning = False

    if current_warning:
        warnings.append((log_file_path, "".join(current_warning).strip()))

    return warnings


def generate_summary_table(total_logs, errors_found, warnings_found, clean_logs):
    return (
        f"\n### **Log Processing Summary**\n\n"
        f"| **Total Logs Processed** | **Errors Found** | **Warnings Found** | **Clean Logs** |\n"
        f"|--------------------------|------------------|--------------------|----------------|\n"
        f"| **{total_logs}**                   | 🔴 **{errors_found}**         | 🟡 **{warnings_found}**           | ✅ **{clean_logs}**       |\n"
        "---\n"
    )


def generate_breakdown_table(header, icon, logs, category):
    """
    Generates a Markdown summary table for log processing statistics.

    Args:
        total_logs (int): Total number of logs processed.
        errors_found (int): Total number of errors found.
        warnings_found (int): Total number of warnings found.
        clean_logs (int): Total number of clean logs (no errors or warnings).

    Returns:
        str: The generated summary table in Markdown format.
    """
    if not logs:
        return ""

    every_parsed_log = {}

    for each_log in logs:
        if isinstance(each_log, tuple) and len(each_log) == 2:
            is_log_path, is_log_name = each_log
        else:
            raise ValueError(f"Unexpected log format: {each_log}")

        if is_log_path not in every_parsed_log:
            every_parsed_log[is_log_path] = []
        every_parsed_log[is_log_path].append(is_log_name)

    report_parts = []

    for is_log_path, log_lines in every_parsed_log.items():
        log_name = os.path.basename(is_log_path)

        table = (
            f"\n#### **{header} - {log_name}**\n"
            f"| **{category}**                   | **Location**                                            |\n"
            f"|----------------------------------|---------------------------------------------------------|\n"
        )

        row_count = 0
        for is_log_name in log_lines:
            flattened_log = is_log_name.replace("\n", " ").strip()
            table += f"| {icon} {flattened_log}                | `{is_log_path}`                                            |\n"
            row_count += 1

        # Append the row count at the end of the table
        table += f"| **Exceptions Caught:** |    {row_count}                                                    |\n"
        report_parts.append(table + "---\n")

    return "".join(report_parts)


def process_logs_with_progress(log_files):
    """
    Processes a list of log files while displaying progress, classifying errors, warnings, and clean logs.

    Args:
        log_files (list): A list of log file paths to process.

    Returns:
        tuple: Aggregated counts of errors, warnings, clean logs, and detailed lists of each type.
    """
    sum_of_exceptions = len(log_files)
    total_errors = 0
    total_warnings = 0
    total_clean_logs = 0

    error_logs_list = []
    warning_logs_list = []
    clean_logs_list = []

    with Progress() as progress:
        task = progress.add_task("[green]Processing logs...", total=sum_of_exceptions)

        for each_log_file_path in log_files:
            time.sleep(0.03)

            log_name = os.path.basename(each_log_file_path)

            if log_name == "redscript_rCURRENT.log":
                log_warnings = classify_redscript_log(each_log_file_path)
                log_errors = []
            else:
                log_errors, log_warnings = classify_log_entries(each_log_file_path)

            if log_errors:
                total_errors += len(log_errors)
                error_logs_list.extend(log_errors)
            if log_warnings:
                total_warnings += len(log_warnings)
                warning_logs_list.extend(log_warnings)
            if not log_errors and not log_warnings:
                total_clean_logs += 1
                clean_logs_list.append((log_name, each_log_file_path))

            progress.advance(task)

    # Ensure exactly 6 return values
    return (
        total_errors,
        total_warnings,
        total_clean_logs,
        error_logs_list,
        warning_logs_list,
        clean_logs_list,
    )


def process_log_files_in_directory(game_directory_path):
    """
    Orchestrates log file processing by scanning a given game directory for log files and generating a report.

    Args:
        game_directory_path (str): The path to the game directory containing log files.

    Returns:
        str: A full report in Markdown format summarizing errors, warnings, and clean logs.
    """
    log_files = []

    IS_REDSCRIPT_LOG = r"G:\Steam Library\steamapps\common\Cyberpunk 2077\r6\logs\redscript_rCURRENT.log"

    for each_directory, _, each_log_file in os.walk(game_directory_path):
        log_paths = [
            os.path.join(each_directory, each_log)
            for each_log in each_log_file
            if each_log.endswith(".log")
        ]
        if (
            each_directory == os.path.dirname(IS_REDSCRIPT_LOG)
            and os.path.basename(IS_REDSCRIPT_LOG) in each_log_file
        ):
            log_files.append(IS_REDSCRIPT_LOG)
        else:
            log_files.extend(log_paths)

    error, warning, clean_logs, error_logs, warning_logs, list_of_clean_logs = (
        process_logs_with_progress(log_files)
    )

    report_sections = []
    report_sections.append(
        generate_summary_table(
            len(log_files), len(error_logs), len(warning_logs), clean_logs
        )
    )
    report_sections.append(
        generate_breakdown_table("Error Breakdown", "🔴", error_logs, "Error Logs")
    )
    report_sections.append(
        generate_breakdown_table(
            "Warning Breakdown", "🟡", warning_logs, "Warning Logs"
        )
    )

    if list_of_clean_logs:
        log_list_to_md_table = (
            "\n#### **Clean Logs Breakdown**\n"
            "| **Log Name**                   | **Location**                                            |\n"
            "|--------------------------------|---------------------------------------------------------|\n"
        )
        for each_log_file_name, each_log_file_path in list_of_clean_logs:
            log_list_to_md_table += f"| ✅ {each_log_file_name}                | `{each_log_file_path}`                                            |\n"

        report_sections.append(log_list_to_md_table + "---\n")

    return "".join(report_sections)


if __name__ == "__main__":
    GAME_DIRECTORY_PATH = r"G:\Steam Library\steamapps\common\Cyberpunk 2077"
    markdown_analysis_report = process_log_files_in_directory(GAME_DIRECTORY_PATH)

    with open("Log File Analysis.md", "w", encoding="utf-8") as markdown_file:
        markdown_file.write(markdown_analysis_report)

    rprint(
        f"\n[green]Success! ✅ Your markdown report has been generated: Log_Report_Analysis.md[/green]"
    )
