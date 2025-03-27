from pathlib import Path

class Browser:
    """Classe pour les navigateurs"""

    def __init__(self, name: str, user_data_path: Path):
        self.name = name
        self.user_data_path = user_data_path
        self.local_state_path = user_data_path / "Local State"
        self.profiles = []  # Liste pour stocker les profils associés
        self.encryption_key = None

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"Browser({self.name}, {self.user_data_path})"

    def add_profile(self, profile: "Profile"):
        """Ajoute un profil au navigateur"""
        self.profiles.append(profile)


class Profile:
    """Classe pour les profils des navigateurs
    """
    def __init__(self, name: str, path: Path):
        self.name = name
        self.profile_path = path
        self.password_paths = []
        self.history_paths = []
        self.credit_cards_paths = []
        self.cookies_path = []
        self.bookmarks_path = []
        self.extensions_path = []
        self.web_data_path = []

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Profile({self.name}, {self.profile_path})"
    
    def set_profile_path(self, path: Path):
        self.profile_path.append(path)

    def set_password_path(self, path: Path):
        self.password_paths.append(path)

    def set_history_path(self, path: Path):
        self.history_paths.append(path)

    def set_credit_cards_path(self, path: Path):
        self.credit_cards_paths.append(path)

    def set_cookies_path(self, path: Path):
        self.cookies_path.append(path)

    def set_bookmarks_path(self, path: Path):
        self.bookmarks_path.append(path)

    def set_extensions_path(self, path: Path):
        self.extensions_path.append(path)

    def set_web_data_path(self, path: Path):
        self.web_data_path.append(path)