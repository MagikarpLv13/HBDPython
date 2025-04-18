import sys
import csv
import config
import os
import flet as ft
import time

IS_WINDOWS = False
IS_LINUX = False
IS_MAC = False
LOG = None
PAGE = None

def set_platform():
    global IS_WINDOWS, IS_LINUX, IS_MAC
    # Vérification de l'OS
    IS_WINDOWS = sys.platform.startswith("win")
    IS_LINUX = sys.platform.startswith("linux")
    IS_MAC = sys.platform.startswith("darwin")

# Transforme la data en csv
def write_to_csv(data, file_name, browser_name:str, profile_name:str = None) -> None:
    """
    Write data from a cursor.fetchall() result to a CSV file.
    :param data: List of tuples representing rows of data.
    :param file_name: Name of the CSV file to write to.
    """
    if not data:
        raise ValueError("Data is empty. Cannot write to CSV.")

    # Extraire les noms de colonnes à partir de la première ligne de données
    if isinstance(data[0], dict):
        fieldnames = data[0].keys()
    else:
        raise ValueError("Data must be a list of dictionaries.")

    if profile_name:
        file_path = os.path.join(config.DEFAULT_RESULT_PATH, browser_name, profile_name, file_name)
    else:
        file_path = os.path.join(config.DEFAULT_RESULT_PATH, browser_name, file_name)

    create_destination_folder(file_path)

    add_to_log(f"✏️ Écriture des résultats dans {file_path}...", style="info")
    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Creer le dossier de destination si il n'existe pas
def create_destination_folder(path):
    """
    Check if the destination folder exists, if not create it.
    :param destination_folder: Path to the destination folder.
    """
    if not os.path.exists(path):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        except OSError as e:
            raise OSError(f"Error creating directory: {e}")
       
# Fonction pour ajouter un message au log
def add_to_log(message: str, style: str = None):
    """
    Add a message to the log display.
    :param message: Message to log.
    """
    color_map = {
        "info": ft.Colors.BLUE_300,
        "error": ft.Colors.RED_300,
        "success": ft.Colors.GREEN_300,
        None: ft.Colors.GREY_300
    }

    log_message = ft.Text(message, color=color_map.get(style, ft.Colors.GREY_300))

    if LOG:
        LOG.controls.append(log_message)
        LOG.scroll_to(-1, duration=0.05)
        time.sleep(0.05)
        PAGE.update()
