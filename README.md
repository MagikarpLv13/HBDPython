# HBDPython

HBDPython est une implémentation en Python inspirée de **HackBrowserData**. Cet outil permet d'extraire et d'analyser les données sensibles stockées par les navigateurs Web. Il fonctionne sur **Windows, Linux et macOS**, prenant en charge les navigateurs **Chromium** et **Firefox**. Les données récupérées sont au format **CSV**.

## ✨ Fonctionnalités
- Récupération des **mots de passe enregistrés**
- Extraction de l'**historique de navigation**
- Sauvegarde des **favoris (bookmarks)**
- Récupération des **cartes bancaires enregistrées**
- Extraction de l'**historique de téléchargement**
- Accès au **localStorage**
- Liste des **extensions installées**

## 🚀 Compatibilité
### **Systèmes d'exploitation supportés**
- Windows
- Linux
- macOS

### **Navigateurs compatibles**
#### 🦄 Basés sur Chromium :
- Google Chrome
- Brave
- Microsoft Edge
- Opera
- Vivaldi

#### 🧠 Firefox :
- Mozilla Firefox

## ⚡ Installation

### 1. Cloner le projet
```bash
git clone https://github.com/MagikarpLv13/HBDPython.git
cd HBDPython
```

### 2. Créer un environnement virtuel
#### Sur Windows :
```bash
python -m venv venv
venv\Scripts\activate
```
#### Sur Linux/macOS :
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

## 🛠️ Utilisation
Lance le script principal pour commencer l'extraction des données :
```bash
python main.py
```

## 📘 Licence
Ce projet est à usage **éducatif** uniquement.

---

⚠ **Avertissement :** L'utilisation de cet outil pour collecter des données personnelles sans consentement est une violation des lois sur la protection des données. Ce projet est destiné à des fins de test et de recherche en cybersécurité. Toute utilisation illégale relève de la seule responsabilité de l'utilisateur, et les développeurs ne pourront être tenus responsables de toute infraction aux lois en vigueur.
