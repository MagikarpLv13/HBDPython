import os
from pathlib import Path

# Définition des navigateurs Chromium supportés et le chemin des profils par défaut sur chaque système
CHROMIUM_BROWSERS = {
    "browser": {
        "Google Chrome": {
            "windows": Path(os.getenv("LOCALAPPDATA"))
            / "Google"
            / "Chrome"
            / "User Data",
            "linux": Path.home() / ".config" / "google-chrome",
            "mac": Path.home()
            / "Library"
            / "Application Support"
            / "Google"
            / "Chrome",
        },
        "Brave": {
            "windows": Path(os.getenv("LOCALAPPDATA"))
            / "BraveSoftware"
            / "Brave-Browser"
            / "User Data",
            "linux": Path.home() / ".config" / "BraveSoftware" / "Brave-Browser",
            "mac": Path.home()
            / "Library"
            / "Application Support"
            / "BraveSoftware"
            / "Brave-Browser",
        },
        "Microsoft Edge": {
            "windows": Path(os.getenv("LOCALAPPDATA"))
            / "Microsoft"
            / "Edge"
            / "User Data",
            "linux": Path.home() / ".config" / "microsoft-edge",
            "mac": Path.home() / "Library" / "Application Support" / "Microsoft Edge",
        },
        "Opera": {
            "windows": Path(os.getenv("APPDATA")) / "Opera Software" / "Opera Stable",
            "linux": Path.home() / ".config" / "opera",
            "mac": Path.home() / "Library" / "Application Support" / "Opera",
        },
        "Vivaldi": {
            "windows": Path(os.getenv("LOCALAPPDATA")) / "Vivaldi" / "User Data",
            "linux": Path.home() / ".config" / "vivaldi",
            "mac": Path.home() / "Library" / "Application Support" / "Vivaldi",
        },
    },
    "db" : {
        "history": "History",
        "cookies": "Network/Cookies",
        "bookmarks": "Bookmarks",
        "credit_cards": "Web Data",
        "extensions": "Extensions",
        "logins": ["Login Data", "Login Data For Account"],
        "local_storage": "Local Storage/leveldb",
    }
}

FIREFOX_PATH = {
    "windows": Path(os.getenv("APPDATA")) / "Mozilla" / "Firefox" / "Profiles",
    "linux": Path.home() / ".mozilla" / "firefox",
    "mac": Path.home() / "Library" / "Application Support" / "Firefox",
}
