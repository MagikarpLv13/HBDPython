import os
from pathlib import Path

# Configuration du chemin par défaut pour les résultats
DEFAULT_RESULT_PATH = Path.home() / "HBDPython" / "browser-data-extractor"

# Dossier de profil customisé par l'utilisateur
CUSTOM_PROFILE_PATH = ""

OPTIONS = {
    "passwords" : {
        "name": "Mots de passe",
        "description": "Récupérer les mots de passe enregistrés",
        "default": True,
        "active": True,
    },
    "credit_cards" : {
        "name": "Cartes de crédit",
        "description": "Récupérer les cartes de crédit enregistrées",
        "default": True,
        "active": True,
    },
    "cookies" : {
        "name": "Cookies",
        "description": "Récupérer les cookies",
        "default": True,
        "active": True,
    },
    "bookmarks" : {
        "name": "Favoris",
        "description": "Récupérer les favoris",
        "default": True,
        "active": True,
    },
    "extensions" : {
        "name": "Extensions",
        "description": "Récupérer les extensions installées",
        "default": True,
        "active": True,
    },
    "history" : {
        "name": "Historique",
        "description": "Récupérer l'historique de navigation",
        "default": True,
        "active": True,
    },
    "download_history" : {
        "name": "Historique de téléchargement",
        "description": "Récupérer l'historique de téléchargement",
        "default": True,
        "active": True,
    },
    "local_storage" : {
        "name": "Stockage local",
        "description": "Récupérer le stockage local",
        "default": True,
        "active": True,
    },
}

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
