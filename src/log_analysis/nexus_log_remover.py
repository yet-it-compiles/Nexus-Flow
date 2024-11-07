import os
import json
from pathlib import Path
from rich import print as rprint
from rich.progress import Progress
from tkinter import Tk, filedialog

CONFIG_FILE = "config.json"


def load_config():
    """
    Loads the game directory path from the configuration file.

    Returns:
        str | None: Path to the game directory if loaded successfully, None otherwise.
    """
    try:
        with open(CONFIG_FILE, "r") as config_file:
            config = json.load(config_file)
            game_directory = config.get("game_directory")

            if not game_directory or not os.path.exists(game_directory):
                print(
                    "Game directory not found in configuration. Setting up configuration..."
                )
                return create_config(config)

            return game_directory

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
    game_directory = config.get("game_directory")
    if not game_directory or not os.path.exists(game_directory):
        game_directory = input("Enter the full path to the game directory: ").strip()
        if os.path.exists(game_directory):
            config["game_directory"] = game_directory
            with open(CONFIG_FILE, "w") as config_file:
                json.dump(config, config_file, indent=4)
            print(f"Game directory path saved to {CONFIG_FILE}.")
        else:
            print(
                "The provided game directory path does not exist. Please restart and enter a valid path."
            )
            return None

    return game_directory


def read_load_order(load_order_path):
    try:
        with open(load_order_path, "r") as load_order_file:
            return [line.strip() for line in load_order_file]
    except (FileNotFoundError, IOError) as e:
        rprint(f"[bold red][ERROR][/bold red] Failed to read load order: {e}")
        return []


def write_load_order(load_order_path, archive_list):
    try:
        with open(load_order_path, "w") as load_order_file:
            load_order_file.writelines(f"{archive}\n" for archive in archive_list)
    except IOError as e:
        rprint(f"[bold red][ERROR][/bold red] Failed to write load order: {e}")


def apply_custom_mod_order_rules(archive_list, custom_order_rules):
    """
    Apply custom load order rules to the list of mods, ensuring all mods in each rule exist in the list.

    Args:
        archive_list (list): List of mod filenames.
        custom_order_rules (dict): Dictionary with mods as keys and their dependencies as values.

    Returns:
        tuple: A tuple containing the reordered mod list and the count of overridden mods.
    """
    ordered_mods, overridden_count = [], 0
    archive_set = set(archive_list)

    # Filter rules based on existing files in the mod list
    filtered_order_rules = {
        each_mod: each_dependency
        for each_mod, each_dependency in custom_order_rules.items()
        if each_mod in archive_set
        and all(dep in archive_set for dep in each_dependency)
    }

    # Process each mod and its dependencies in the filtered rules
    for each_mod, each_mod_dependency in filtered_order_rules.items():
        for each_mod_required in each_mod_dependency:
            if each_mod_required in archive_set:
                archive_set.remove(each_mod_required)
                ordered_mods.append(each_mod_required)
                overridden_count += 1

    remaining_archives = sorted(archive_set)

    # Insert mods from the filtered rules at their target positions
    for each_mod, each_mod_dependency in filtered_order_rules.items():
        index = (
            remaining_archives.index(each_mod)
            if each_mod in remaining_archives
            else len(remaining_archives)
        )
        for each_mod_required in reversed(each_mod_dependency):
            remaining_archives.insert(index, each_mod_required)

    return remaining_archives, overridden_count


def get_modlist_path():
    Tk().withdraw()
    rprint(
        "[bold yellow][INFO][/bold yellow] Please select the [cyan]modlist.txt[/cyan] file..."
    )
    return Path(
        filedialog.askopenfilename(
            title="Select modlist.txt", filetypes=[("Text Files", "*.txt")]
        )
    )


def manage_mod_load_order():
    CONFIG_FILE = load_config() or get_modlist_path()
    if not CONFIG_FILE:
        print(
            "[bold red][ERROR][/bold red] No valid [cyan]modlist.txt[/cyan] file found or selected."
        )
        return
    create_config(CONFIG_FILE)

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

        initial_load_order = read_load_order(CONFIG_FILE)
        if not initial_load_order:
            print(f"[bold yellow][INFO][/bold yellow] No valid load order found.")
            return

        progress.update(task, advance=50)
        final_order, overridden_count = apply_custom_mod_order_rules(
            initial_load_order, custom_order_rules
        )
        progress.update(task, advance=30)

        write_load_order(CONFIG_FILE, final_order)
        progress.update(task, advance=20)

        rprint(
            f"[bold green][SUCCESS][/bold green] Custom load order applied for [cyan]{
                overridden_count}[/cyan] mod(s) in [cyan]modlist.txt[/cyan]."
        )
        os.startfile(CONFIG_FILE)


if __name__ == "__main__":
    manage_mod_load_order()
