import os
import json
import shutil

CONFIG_FILE = "config.json"


def load_game_root_from_config():
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


def remove_all_logs(source_directory, target_directory, totoal_logs_removed):
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    totoal_logs_removed = 0

    for each_folder, each_file in os.walk(source_directory):
        for each_log in each_file:
            if each_log.lower().endswith(".log"):
                source_path = os.path.join(each_folder, each_log)
                target_path = os.path.join(target_directory, each_log)

                try:
                    shutil.move(source_path, target_path)
                    print(f"- Moved: {source_path} -> {target_path}\n")
                    totoal_logs_removed += 1
                except Exception as exception:
                    print(f"Error moving {source_path}: {exception}")

    return totoal_logs_removed


if __name__ == "__main__":
    is_source_directory = load_game_root_from_config()

    if is_source_directory is None:
        is_source_directory = input("Please enter the game root folder path: ")

    target_directory = input(
        "Please enter the target directory path for relocated log files: "
    )

    total_logs_removed = remove_all_logs(is_source_directory, target_directory)
    print("All .log files have been moved to the new directory.")
    print(f"Total files moved: {total_logs_removed}")
