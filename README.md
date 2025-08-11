# OC-Projet12 : Développez une architecture back-end sécurisée avec Python et SQL.

Cette application est un CRM avec une interface CLI qui permet à ses utilisateurs de :<br>
- Créer et gérer des clients <br>
- Créer et gérer des contrats associés au client <br>
- Créer et gérer des évènements associés au contrat <br>
<br>

> [!NOTE]
> Testé sous Ubuntu 24.04 - Python 3.12.3 - MySQL 8.0.42

## ✅ Prérequis

Pour installer ce programme, vous aurez besoin d'une connexion internet. Le programme est ensuite exécuté en local et ne nécessite pas de connexion internet pour fonctionner.<br>
<br>
Python doit être installé sur votre ordinateur (version 3.12.3 ou supérieur).<br>
<br>
MySQL doit également être installé sur votre poste (version 8.0.42 ou supérieur).<br>
<br>
L'installateur **pip** doit également être disponible sur votre machine pour installer les dépendances.
Il est possible d'utiliser **pipenv** pour centraliser la gestion des modules, dépendances et environnement virtuel.

## 📦 Installation et exécution du programme

<details>
<summary>📍 Etape 1 - Installer git</summary><br>

Pour télécharger ce programme, vérifiez que git est bien installé sur votre poste.<br>
Vous pouvez l'installer en suivant les instructions fournies sur le site [git-scm.com](https://git-scm.com/book/fr/v2/D%C3%A9marrage-rapide-Installation-de-Git)

</details>

<details>
<summary>📍 Etape 2 - Cloner le dépôt contenant le programme</summary><br>


Placez-vous dans le dossier souhaité et utilisez la commande suivante :

``git clone https://github.com/Guillaume-Gillon/OC_Projet12.git``

</details>

<details>
<summary>📍 Etape 3 - Créer et activer un evironnement virtuel</summary><br>

Créez un environnement virtuel avec la commande<br>
``python3 -m venv env``<br>

Activez cet environnement avec la commande<br>
``source env/bin/activate``

</details>

<details>
<summary>📍 Etape 4 - Installer les dépendances</summary><br>

Pour que ce programme s'exécute, vous aurez besoin de plusieurs packages additionnels listés dans le fichier requirements.txt.<br>

Exécutez la commande <br>
``pip install -r requirements.txt``

</details>

<details>
<summary>📍 Etape 5 - Créer un utilisateur MySQL ayant des droits d'administration</summary><br>

Connectez-vous en root à MySQL et exécutez les commandes suivantes : <br>
``CREATE USER 'admin_EpicEventsCRM'@'localhost' IDENTIFIED BY 'mot_de_passe';``<br>
``GRANT ALL PRIVILEGES ON *.* TO 'admin_EpicEventsCRM'@'localhost' WITH GRANT OPTION;``<br>
``FLUSH PRIVILEGES;``

> Remplacer 'mot_de_passe' par votre mot de passe fort

</details>

<details>
<summary>📍 Etape 6 - Initialisation de la base de données</summary><br>

Exécutez la commande suivante :<br>
``python3 install.py``

</details>

<details>
<summary>📍 **Etape 7 - Exécution de l'application**</summary><br>

Exécutez la commande suivante :<br>
``python3 main.py``

</details>

## ⚙️ Fonctionnement du programme

L'application comporte différentes sections accessibles sur permission. Le détail de ces permissions est disponible dans le cahier des charges.
<br><br>

## 🗑 Désinstallation

Pour désinstaller le programme, exécuter la commande suivante :<br>
``python3 uninstall.py``
