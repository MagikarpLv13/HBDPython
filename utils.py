import sys
import csv

IS_WINDOWS = False
IS_LINUX = False
IS_MAC = False

def set_platform():
    global IS_WINDOWS, IS_LINUX, IS_MAC
    # Vérification de l'OS
    IS_WINDOWS = sys.platform.startswith("win")
    IS_LINUX = sys.platform.startswith("linux")
    IS_MAC = sys.platform.startswith("darwin")
    
def write_to_csv(data, file_name):
    """
    Write data from a cursor.fetchall() result to a CSV file.
    :param data: List of tuples representing rows of data.
    :param file_name: Name of the CSV file to write to.
    """
    if not data:
        raise ValueError("Data is empty. Cannot write to CSV.")
    
    # Extract column names from the first row's keys if it's a dictionary
    if isinstance(data[0], dict):
        fieldnames = data[0].keys()
    else:
        raise ValueError("Data must be a list of dictionaries.")
    
    with open(file_name, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
