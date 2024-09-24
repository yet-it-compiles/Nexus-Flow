"""
Load Order Sorter Script for Cyberpunk 2077

This script automates the sorting of mod load orders for Cyberpunk 2077 by reading `modlist.txt` file, applying both alphabetical sorting, the users  custom-defined load order rules, and saving the final order back to the file.

Modules:
    - os: Provides functions to interact with the operating system (file management).
    - json: Handles reading and writing of the configuration file in JSON format.
    - pathlib (Path): Manages file paths and directory operations in a cross-platform way.
    - rich.print: Provides rich-text printing capabilities for the console output.
    - tkinter (Tk, filedialog): Facilitates GUI file dialog for user input.
    - rich.progress: Displays a progress bar to track the sorting progress.

Functions:
    - load_config(): Loads the configuration file to retrieve the saved path to `modlist.txt`.
    - save_config(): Saves the path to `modlist.txt` in the configuration file.
    - read_load_order(): Reads the load order from the `modlist.txt` file.
    - write_load_order(): Writes the updated load order back to the `modlist.txt` file.
    - sort_archive_files(): Sorts the mod files in alphabetical ASCII order.
    - apply_custom_mod_order_rules(): Applies user-defined custom sorting rules to reorder mods.
    - show_progress_bar(): Manages the display of the progress bar for task progress.
    - get_modlist_path(): Opens a file dialog for the user to select the `modlist.txt` file.
    - manage_mod_load_order(): Coordinates the full process of loading, sorting, and saving the mod load order.
"""

import os
import json
from pathlib import Path
from rich import print as rprint
from tkinter import Tk, filedialog
from rich.progress import Progress

CONFIG_FILE = "config.json"


def load_config():
    """
    Loads the configuration file to retrieve the saved modlist.txt path.

    Returns:
        str or None: The saved path from the config file, or None if no valid path is found.
    """
    if not os.path.exists(CONFIG_FILE):
        return None

    with open(CONFIG_FILE, "r") as config_file:
        config = json.load(config_file)
        modlist_path = config.get("modlist_path", None)

        if modlist_path and os.path.exists(modlist_path):
            return modlist_path
        return None


def save_config(modlist_path):
    """
    Saves the modlist.txt path to the configuration file for easier future use.

    Args:
        modlist_path (str): The path to modlist.txt to be saved in the config file.
    """
    config = {"modlist_path": str(modlist_path)}
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config, config_file)


def read_load_order(load_order_path):
    """
    Reads the current load order from the 'modlist.txt' file, where the file represents the load order, and each line represents the name of a .archive file representing the mod. This function returns each .archive entry in the order that the game will load them, without newline characters.

    Args:
        load_order_path (str): Full path to the 'modlist.txt' file containing the initial load order.

    Yields:
        str: Each line in the file representing an .archive mod, stripped of newline characters.

    Raises:
        FileNotFoundError: If the 'modlist.txt' file is missing.
        IOError: If the file cannot be read due to access issues.
    """
    try:
        with open(load_order_path, "r") as load_order_file:
            for each_archive_file in load_order_file:
                yield each_archive_file.rstrip("\n")
    except FileNotFoundError:
        print(
            f"[ERROR] Could not find modlist.txt at '{load_order_path}'. Please check the file path and try again."
        )
    except IOError:
        print(
            f"[ERROR] Unable to read modlist.txt at '{load_order_path}'. Ensure the file is accessible."
        )


def write_load_order(load_order_path, archive_list):
    """
    Commits the finalized load order to 'modlist.txt' after applying custom rules or manual reordering.

    Args:
        load_order_path (str): The full path to the 'modlist.txt' file where the updated load order will be saved.
        archive_list (list): A list of .archive filenames representing the final mod load order.

    Raises:
        IOError: If the file cannot be written due to permission or access issues.
    """
    try:
        with open(load_order_path, "w") as load_order_file:
            load_order_file.writelines([archive + "\n" for archive in archive_list])
    except IOError:
        print(
            f"[ERROR] Failed to write to the load order file at '{load_order_path}'. Ensure write permissions are granted."
        )


def sort_archive_files(mod_archive_list):
    """
    Sorts the list of .archive files based on the games default alphebetrical ASCII sorting.

    Args:
        mod_archive_list (list): List of mod .archive filenames to be sorted.

    Returns:
        list: The sorted list of mod .archive filenames, ordered by ASCII sequence.
    """
    return sorted(mod_archive_list)


def apply_custom_mod_order_rules(list_of_archive_files, custom_order_rules):
    """
    Applies the user specified custom load order, allowing the user to choose which mod overwrites another resulting in conflict winning changes

    This function finds and relocates specific mods in the list to the desired positions as defined in the custom load order rules.

    Args:
        archive_list (list): The current list of .archive files that represent the mod load order.
        custom_order_rules (dict): A dictionary where keys are the base mods, and values are lists of priority mods that need to be relocated directly above those base mods.


    Returns:
        tuple:
            - The updated list of .archive filenames with the custom load order applied.
            - The number of mods that were moved to new positions.

    Raises:
        ValueError: If the mod_archive_list contains missing or invalid entries that contradict the rules.
    """
    priority_archive_file = {}
    overridden_mod_count = 0

    # Convert the list to a set for faster lookups
    set_of_archives = set(list_of_archive_files)

    # Collect priority mods to re-order based on the user defined order
    for each_archive_file, custom_sorting_rule in custom_order_rules.items():
        priority_archive_file[each_archive_file] = []
        for each_archive_to_sort in custom_sorting_rule:
            if each_archive_to_sort in set_of_archives:
                priority_archive_file[each_archive_file].append(each_archive_to_sort)
                set_of_archives.remove(each_archive_to_sort)
                overridden_mod_count += 1

    # Sort the remaining archives alphabetically by alphebetical ASCII
    sorted_archive_list = sort_archive_files(list(set_of_archives))

    # Reinsert the specified priority archives according to custom rules
    for each_archive_file, mods in priority_archive_file.items():
        if each_archive_file in sorted_archive_list:
            base_index = sorted_archive_list.index(each_archive_file)
            for each_archive_to_resort in reversed(mods):
                sorted_archive_list.insert(base_index, each_archive_to_resort)
        else:
            sorted_archive_list.extend(mods)

    return sorted_archive_list, overridden_mod_count


def show_progress_bar(progress_task, task_description, total_steps):
    """
    Displays a progress bar to show progress of modlist.txt sort

    Args:
        progress_task (Progress): The progress task being managed.
        task_description (str): A description of the task to display on the progress bar.
        total_steps (int): Total steps the task will complete.
    """
    return progress_task.add_task(f"[green]{task_description}...", total=total_steps)


def get_modlist_path():
    """
    Opens a file dialog to allow the user to select the 'modlist.txt' file.

    Returns:
        Path: The full path to the selected 'modlist.txt' file.
    """
    root = Tk()
    root.withdraw()
    rprint("[yellow][INFO][/yellow] Please select the modlist.txt file...")

    file_path = filedialog.askopenfilename(
        title="Select modlist.txt",
        filetypes=[("Text Files", "*.txt")],
        initialdir=os.path.expanduser("~"),
    )

    if not file_path:
        rprint(
            "[red][ERROR][/red] No file was selected. Please try selecting modlist.txt and try again."
        )
        exit()

    return Path(file_path)


def manage_mod_load_order():
    """
    The function reads the initial 'modlist.txt' file and applies the user specified custom sorting rules. After processing, the 'modlist.txt' is opened so the user can view the changes.

    Raises:
        FileNotFoundError: If the 'modlist.txt' file is missing.
        IOError: If there is an issue reading or writing the mod load order file.
    """
    load_order_path = load_config()

    if load_order_path is None:
        load_order_path = get_modlist_path()
        save_config(load_order_path)

    # Dictionary containing the custom load order the user wants to apply
    custom_order_rules = {
        "!!!!!4k bulletholes.archive": [
            "dxhud_lite.archive",
            "dxhud_quest.archive",
            "dxstreamlined.archive",
        ],
        "!!!Fire FX Extras.archive": ["00Immersive_Flash.archive"],
        "HD Reworked Project.archive": ["Preem Water 2.0 - Pure.archive"],
    }

    # Defines the progress bar, which acts as a representation of how long until the sorting is completed.
    with Progress() as progress:
        sorted_loadorder_result = show_progress_bar(
            progress, "Processing load order", total_steps=100
        )

        # Load the current archive file names / load order from the file
        initial_archive_loadorder = list(read_load_order(load_order_path))

        if not initial_archive_loadorder:
            rprint(
                "[yellow][INFO][/yellow] The load order file appears to be empty or could not be read. Please check the path and try again."
            )
            return

        progress.update(sorted_loadorder_result, advance=50)

        # Apply custom order rules and counts how many files were re-ordered
        sorted_archive_files, overridden_mod_count = apply_custom_mod_order_rules(
            initial_archive_loadorder, custom_order_rules
        )

        progress.update(sorted_loadorder_result, advance=30)

        # Writes the sorted, and custom load order back to modlist.txt
        write_load_order(load_order_path, sorted_archive_files)

        progress.update(sorted_loadorder_result, advance=20)

        rprint(
            f"[green][SUCCESS][/green] Your custom load order was successfully applied for {overridden_mod_count} mod{'s' if overridden_mod_count != 1 else ''} to modlist.txt!"
        )

        # Open modlist.txt for review after sorting
        os.startfile(load_order_path)


if __name__ == "__main__":
    manage_mod_load_order()
