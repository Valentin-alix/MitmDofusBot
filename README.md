# Setup :

- Désactiver l'ipv6 sur votre pc

- Installer Jpexs-decompiler : https://github.com/jindrapetrik/jpexs-decompiler
- Créer un fichier .env dans app/.env , vous pouvez prendre exemple sur le fichier app/.env.template : 
  ```
  D2O_FOLDER="C:\\Users\\valen\\AppData\\Local\\Ankama\\Dofus\\data\\common"
  D2P_FOLDER="C:\\Users\\valen\\AppData\\Local\\Ankama\\Dofus\\content\\gfx\\items"
  D2P_FOLDER2="C:\\Users\\valen\\AppData\\Local\\Ankama\\Dofus\\content\\gfx\\sprites"
  D2I_FILE="C:\\Users\\valen\\AppData\\Local\\Ankama\\Dofus\\data\\i18n\\i18n_fr.d2i"
  DOFUS_INVOKER="C:\\Users\\valen\\AppData\\Local\\Ankama\\Dofus\\DofusInvoker.swf"
  FFDECJAR_PATH="C:\\Program Files (x86)\\FFDec\\ffdec.jar"
  ```
- Lancer init.bat

- Python app/__main__.py # Lance le bot

Vous n'avez plus qu'à connecter votre personnage (vous devez déco/reco si votre personnage est déjà connecté).

# Fonctionnalités :

- Sniffer

- Scrapping de l'hdv
    - Graphique du prix des items au fil du temps
    - Top 10 des meilleurs bénéfices au recyclage des pépites
    - Top 10 des chutes les plus importante de prix

- Automatisation de la vente d'objets en hdv
    - Vente automatique des objets(ressource/consommable/cosmétique) en hdv
    - Modification automatique des prix des objets (ressource/consommable/cosmétique) en hdv

# Technologies :

➡️ 🐍 Python

- SQLAlchemy
- PyQt5

## Interface de scrapping :

![scrapping bot](./resources/scrapping_interface.png)

## Interface des bénéfices par craft :

![scaping craft](./resources/scrapping_craft_interface.png)

## Interface de vente :

![selling bot](./resources/selling_bot.gif)

## Interface du sniffer :

![sniffer](./resources/sniffer_interface.png)
