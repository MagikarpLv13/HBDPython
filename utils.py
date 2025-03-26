import sys

IS_WINDOWS = False
IS_LINUX = False
IS_MAC = False

def set_platform():
    global IS_WINDOWS, IS_LINUX, IS_MAC
    # Vérification de l'OS
    IS_WINDOWS = sys.platform.startswith("win")
    IS_LINUX = sys.platform.startswith("linux")
    IS_MAC = sys.platform.startswith("darwin")
