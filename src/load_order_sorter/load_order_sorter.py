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
    - load_modlist_path(): Loads the configuration file to retrieve the saved path to `modlist.txt`.
    - save_config(config): Saves the path to `modlist.txt` in the configuration file.
    - read_load_order(load_order_path): Reads the load order from the `modlist.txt` file.
    - write_load_order(load_order_path, archive_list): Writes the updated load order back to the `modlist.txt` file.
    - applies_custom_mod_order_rules(archive_list, custom_order_rules): Applies user-defined custom sorting rules to reorder mods.
    - build_custom_load_order(): Coordinates the full process of loading, sorting, and saving the mod load order.
"""

import os
import json
from rich import print as rprint
from rich.progress import Progress

CONFIG_FILE_PATH = "config.json"


def load_modlist_path():
    """
    Loads the configuration file to retrieve the saved modlist.txt path.

    Returns:
        str or None: The saved path from the config file, or None if no valid path is found.
    """
    try:
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config = json.load(config_file)
            modlist_path = config.get("modlist_directory")
            if not modlist_path or not os.path.exists(modlist_path):
                print(
                    "Modlist.txt file not found in configuration. Setting up configuration..."
                )
                return save_config(config)

            return modlist_path

    except (FileNotFoundError, json.JSONDecodeError):
        print("Configuration file missing. Setting up configuration...")
        return save_config({})


def save_config(config):
    """
    Saves the modlist.txt path to the configuration file for easier future use.

    Args:
        modlist_path (str): The path to modlist.txt to be saved in the config file.
    """
    modlist_directory = config.get("modlist_directory")
    if not modlist_directory or not os.path.exists(modlist_directory):
        modlist_directory = input(
            "Enter the full path to the modlist.txt file: "
        ).strip()
        if os.path.exists(modlist_directory):
            config["modlist_path"] = modlist_directory
            with open(CONFIG_FILE_PATH, "w") as config_file:
                json.dump(config, config_file, indent=4)
            print(f"Modlist path saved to {CONFIG_FILE_PATH}.")
        else:
            print(
                "The provided modlist.txt path does not exist. Please restart and enter a valid path."
            )
            return None

    return modlist_directory


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
            return [each_archive.strip() for each_archive in load_order_file]
    except (FileNotFoundError, IOError) as e:
        rprint(f"[ERROR] {e}")
        return []


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
            load_order_file.writelines(f"{archive}\n" for archive in archive_list)
    except IOError as e:
        rprint(f"[ERROR] {e}")


def applies_custom_mod_order_rules(archive_list, custom_order_rules):
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
    total_mods_overridden = 0
    set_of_archives = set(archive_list)

    load_order_rules = {
        each_mod_requirement: each_required_dependencies
        for each_mod_requirement, each_required_dependencies in custom_order_rules.items()
        if each_mod_requirement in set_of_archives
        and all(
            each_required_dependency in set_of_archives
            for each_required_dependency in each_required_dependencies
        )
    }

    custom_load_order = []
    for (
        each_mod_requirement,
        each_required_dependencies,
    ) in load_order_rules.items():
        for each_required_dependency in each_required_dependencies:
            if each_required_dependency in set_of_archives:
                set_of_archives.remove(each_required_dependency)
                custom_load_order.append(each_required_dependency)
                total_mods_overridden += 1

    remaining_archives = sorted(set_of_archives)

    remaining_archives = sorted(set_of_archives)

    for (
        each_mod_requirement,
        each_required_dependencies,
    ) in load_order_rules.items():
        index = (
            remaining_archives.index(each_mod_requirement)
            if each_mod_requirement in remaining_archives
            else len(remaining_archives)
        )
        for each_required_dependency in reversed(each_required_dependencies):
            remaining_archives.insert(index, each_required_dependency)

    final_order = custom_load_order + remaining_archives
    return final_order, total_mods_overridden


def build_custom_load_order():
    modlist_path = load_modlist_path()
    if not modlist_path or not os.path.exists(modlist_path):
        rprint("[ERROR] No valid modlist.txt file found or selected.")
        return

    """
    The custom_order_rules dictionary contains the user-defined rules for the load order of mods. To use it, the mod to be loaded first should be the key, and the mods that should be loaded before it should be in the list of values.

    "key": ["value1", "value2", ...]
    """
    custom_order_rules = {
        "!!!!!4k bulletholes.archive": [
            "dxhud_lite.archive",
            "dxhud_quest.archive",
            "dxstreamlined.archive",
            "dxstreamlined_hudpos.archive",
        ],
        "!!!Fire FX Extras.archive": ["00Immersive_Flash.archive"],
        "HD Reworked Project.archive": ["Preem Water 2.0 - Canon.archive"],
        "Better Surfaces Textures.archive": ["!!!!!4k bulletholes.archive"],
        "Better Surfaces Textures.archive": ["ETO_1.1_4K.archive"],
        "GymfiendTankPatternsXL.archive": ["GymfiendTankXL.archive"],
        "ETO_1.1_4K.archive": [
            "Preem Water 2.0 - Pure.archive",
            "Preem Shores.archive",
        ],
        "HD Reworked Project.archive": ["TreesVegetations.archive"],
        "00_0MASCV_shoe patch.archive.archiv": [
            "meluminary_mascv_bovver_boot_gymfiend.archive",
            "meluminary_mascv_elegant_shoes_gymfiend.archive",
        ],
        "basegame_texture_HanakoNoMakeup.archive": ["zz-NPCs-Hanako.archive"],
    }

    with Progress() as progress:
        task = progress.add_task("[green]Processing load order...", total=100)

        initial_load_order = read_load_order(modlist_path)
        if not initial_load_order:
            rprint("\n[yellow][INFO][/yellow] No valid load order found.")
            return

        progress.update(task, advance=50)
        final_order, overridden_count = applies_custom_mod_order_rules(
            initial_load_order, custom_order_rules
        )
        progress.update(task, advance=30)

        write_load_order(modlist_path, final_order)
        progress.update(task, advance=20)

    rprint(
        f"[green][SUCCESS][/green] Custom load order applied for {overridden_count} mod(s) in modlist.txt."
    )
    os.startfile(modlist_path)


if __name__ == "__main__":
    build_custom_load_order()
