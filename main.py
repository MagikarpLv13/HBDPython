import os
import platform

def detect_os():
    system = platform.system()  # Récupère le nom du système (Windows, Linux, Darwin...)
    return system

def get_installed_browsers(): # Récupère le nom des navigateurs installés sur la machine
    system = detect_os()
    browsers = []

    if system == "Windows":
        # Vérifier les navigateurs courants sur Windows
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
        firefox_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
        opera_path = "C:\\Program Files\\Opera\\launcher.exe"
        
        # Ajouter les navigateurs installés dans la liste
        if os.path.exists(chrome_path):
            browsers.append("Google Chrome")
        if os.path.exists(edge_path):
            browsers.append("Microsoft Edge")
        if os.path.exists(firefox_path):
            browsers.append("Mozilla Firefox")
        if os.path.exists(opera_path):
            browsers.append("Opera")

    elif system == "Linux":
        # Chemins communs sur différentes distributions Linux
        chrome_paths = ["/usr/bin/google-chrome", "/usr/local/bin/google-chrome", "/snap/google-chrome"]
        firefox_paths = ["/usr/bin/firefox", "/usr/local/bin/firefox", "/snap/firefox"]
        opera_paths = ["/usr/bin/opera", "/usr/local/bin/opera", "/snap/opera"]

        # Vérifier si les navigateurs sont installés dans l'un des chemins
        for path in chrome_paths:
            if os.path.exists(path):
                browsers.append("Google Chrome")
                break  # Si trouvé, sortir de la boucle
        for path in firefox_paths:
            if os.path.exists(path):
                browsers.append("Mozilla Firefox")
                break
        for path in opera_paths:
            if os.path.exists(path):
                browsers.append("Opera")
                break

    elif system == "Darwin":  # macOS
        # Vérifier les navigateurs courants sur macOS
        chrome_path = "/Applications/Google Chrome.app"
        firefox_path = "/Applications/Firefox.app"
        opera_path = "/Applications/Opera.app"
        
        # Ajouter les navigateurs installés dans la liste
        if os.path.exists(chrome_path):
            browsers.append("Google Chrome")
        if os.path.exists(firefox_path):
            browsers.append("Mozilla Firefox")
        if os.path.exists(opera_path):
            browsers.append("Opera")

    else:
        print("Système non pris en charge.")
        return []

    return browsers

def main(): #Fonction principale
    installed_browsers = get_installed_browsers()
    if installed_browsers:
        print(f"Navigateurs installés : {', '.join(installed_browsers)}")
    else:
        print("Aucun navigateur détecté.")

if __name__ == "__main__":
    main()
