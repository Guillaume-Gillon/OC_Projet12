import Model.DB_connect_config as DB_connect_config
from Controller.password_manager import check_password_strength

import mysql.connector
import getpass
import os
import re

"""
** Un utilisateur doit être créé sur le serveur MySQL avant l'exécution de ce script **
CREATE USER 'admin_EpicEventsCRM'@'localhost' IDENTIFIED BY 'mot_de_passe';
GRANT ALL PRIVILEGES ON *.* TO 'admin_EpicEventsCRM'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
"""


class DatabaseConfigurator:
    def __init__(self):
        self._db_name = "EpicEvents_CRM"
        self._admin_username = "admin_EpicEventsCRM"
        self._username = "user_EpicEventsCRM"
        self._user_config_file = "Config/user_config.env"
        self._default_host = "localhost"
        self._admin_data = {}
        self._admin_password = ""
        self._user_password = ""
        self._db_conn = None
        self._cursor = None

    def _create_config_file(self, username, password, config_file) -> bool:
        if os.path.exists(self._user_config_file):
            write_file = input(
                f"{self._user_config_file} existe déjà. Le remplacer? (O/n) : "
            )
            if not write_file == "O":
                print("Le fichier de configuration existant ne sera pas remplacé.")
                return False
        print(f"Création du fichier {config_file} ...")
        if password:
            env_data = f"""
DB_HOST={self._default_host}
DB_PORT=3306
DB_USER={username}
DB_PASSWORD={password}
DB_NAME={self._db_name}
"""
            try:
                with open(config_file, "w") as f:
                    f.write(env_data.strip())
                print(f"Le fichier '{config_file}' a été créé avec succès !")
                return True
            except IOError as e:
                print(
                    f"ERREUR : Impossible de créer le fichier de configuration '{config_file}'. {e}"
                )
                return False

    def _connect_on_server_as_admin(self) -> bool:
        print(f"Connexion de {self._admin_username} en cours ...")
        self._admin_data["username"] = self._admin_username
        self._admin_data["password"] = self._admin_password
        self._db_conn, self._cursor = DB_connect_config.db_connect(self._admin_data)
        if self._db_conn and self._cursor:
            return True
        return False

    def _get_password_from_user(self, username) -> str:
        same_password = False
        while not same_password:
            valid_password = False
            while not valid_password:
                print()
                print(f"Entrez le mot de passe pour l'utilisateur '{username}'")
                password = getpass.getpass(
                    "(min 12 car. dont chiffre + miniscule + majuscule + car. spé.) : "
                )
                valid_password = check_password_strength(password)
                if username == self._admin_username:
                    same_password = True
                else:
                    password_again = getpass.getpass("Confirmez le mot de passe : ")
                    if password == password_again:
                        same_password = True
                    else:
                        print("ERREUR : Les mots de passe ne correspondent pas.")
        return password

    def _ensure_database_exists(self) -> bool:
        if self._cursor:
            query = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s"
            self._cursor.execute(query, (self._db_name,))
            return bool(self._cursor.fetchall())
        return False

    def _create_database(self) -> bool:
        print(f"Création de la base '{self._db_name}' ...")
        try:
            if re.match(r"^[a-zA-Z0-9_]+$", self._db_name):
                # La variable est sûre
                query = f"CREATE DATABASE IF NOT EXISTS {self._db_name};"
                self._cursor.execute(query)
            else:
                # Gérer l'erreur, par exemple en levant une exception
                raise ValueError(
                    "Le nom de la base de données contient des caractères invalides."
                )
            try:
                self._db_conn.commit()
            except mysql.connector.Error as err:
                self._db_conn.rollback()
                print(
                    f"Erreur lors de la transaction. Annulation des modifications : {err}"
                )
            if self._ensure_database_exists():
                print(f"La base '{self._db_name}' a bien été créée.")
                return True
        except Exception as e:
            print(f"Erreur lors de la création de base de données : {e}")
            return False

    def _ensure_user_exists(self) -> bool:
        if self._cursor:
            query = "SELECT User, Host FROM mysql.user WHERE User = %s AND Host = %s"
            self._cursor.execute(query, (self._username, self._default_host))
            return bool(self._cursor.fetchall())

    def _create_user(self) -> bool:
        print(
            f"Création de l'utilisateur '{self._username}'@'{self._default_host}' ..."
        )
        self._user_password = self._get_password_from_user(self._username)
        try:
            query_create_user = "CREATE USER IF NOT EXISTS %s@%s IDENTIFIED BY %s;"
            self._cursor.execute(
                query_create_user,
                (self._username, self._default_host, self._user_password),
            )
            pattern = r"^[a-zA-Z0-9_]+$"
            if (
                re.match(pattern, self._db_name)
                and re.match(pattern, self._username)
                and re.match(pattern, self._default_host)
            ):
                query_grant_user = f"GRANT SELECT, INSERT, UPDATE, DELETE ON {self._db_name}.* TO '{self._username}'@'{self._default_host}'"
                self._cursor.execute(query_grant_user)
                self._cursor.execute("FLUSH PRIVILEGES;")
            else:
                raise ValueError(
                    "Le nom de la base de données, de l'utilisateur ou de l'hôte contient des caractères invalides."
                )
            try:
                self._db_conn.commit()
            except mysql.connector.Error as err:
                self._db_conn.rollback()
                print(
                    f"Erreur lors de la transaction. Annulation des modifications : {err}"
                )
            print(
                f"L'utilisateur {self._username}'@'{self._default_host} a bien été créé !"
            )
            self._create_config_file(
                self._username, self._user_password, self._user_config_file
            )
            return True
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur  : {e}")
            return False

    def run_setup(self) -> bool:
        # Orchestrateur principal de la classe
        # Appelle les méthodes dans l'ordre, gère les retours et les déconnexions

        self._admin_password = self._get_password_from_user(self._admin_username)

        if self._connect_on_server_as_admin():
            print(f"Connecté au serveur MySQL : version {self._db_conn.server_info}")
            print("Vérification de l'existence de la base de données ...")
            if self._ensure_database_exists():
                print(f"La base de données '{self._db_name}' existe déjà !")
                return False
            else:
                if not self._create_database():
                    DB_connect_config.db_disconnect(self._cursor, self._db_conn)
                    return False

            print(f"Vérification de l'existence de l'utilisateur {self._username} ...")
            if not self._ensure_user_exists():
                if not self._create_user():
                    DB_connect_config.db_disconnect(self._cursor, self._db_conn)
                    return False
            else:
                print(
                    f"L'utilisateur '{self._username}'@'{self._default_host}' existe déjà."
                )
                print("Ses privilèges doivent être vérifiées manuellement !")
        else:
            print("Erreur lors de la connexion !")
        return True

    def get_data(self) -> dict:
        data = {
            "db_name": self._db_name,
            "cursor": self._cursor,
            "db_conn": self._db_conn,
            "admin_username": self._admin_username,
            "host": self._default_host,
            "admin_password": self._admin_password,
        }
        return data

    def run_uninstall(self):
        confirmation = input(
            "TOUTES LES DONNEES VONT ETRE SUPPRIMEES! Continuer? (O/n) : "
        )
        if confirmation == "O":
            self._admin_password = self._get_password_from_user(self._admin_username)

            if self._connect_on_server_as_admin():
                print(
                    f"Connecté au serveur MySQL : version {self._db_conn.server_info}"
                )
                print("Vérification de la base de données ...")
                if self._ensure_database_exists():
                    print("Suppression de la base de données ...")
                    query_drop_db = f"DROP DATABASE IF EXISTS {self._db_name}"
                    self._cursor.execute(query_drop_db)
                else:
                    print("La base de données n'existe pas.")
                print(f"Vérification de l'utilisateur '{self._username}' ...")
                if self._ensure_user_exists():
                    print("Suppression de l'utilisateur ...")
                    query_drop_user = "DROP USER IF EXISTS %s@%s"
                    self._cursor.execute(
                        query_drop_user, (self._username, self._default_host)
                    )
                else:
                    print("L'utilisateur n'existe pas.")
                print(f"Vérification du fichier de configuration utilisateur ...")
                if os.path.exists(self._user_config_file):
                    print("Suppression du fichier ...")
                    os.remove(self._user_config_file)
                else:
                    print("Le fichier n'existe pas.")
                return True
        return None
