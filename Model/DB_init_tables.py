from Model.tables import BASE
from Controller import permission_manager

from sqlalchemy import create_engine
import mysql.connector


def create_tables(user, password, host, db_name):

    engine = create_engine(
        f"mysql+mysqlconnector://{user}:{password}@{host}/{db_name}",
        echo=True,
    )
    BASE.metadata.create_all(engine)


def create_unassigned_user(cursor, connexion):
    user_values = ("0", "Unassigned", "Element", "", "")
    query = "INSERT INTO users (employee_number, first_name, last_name, email, password_hash) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (user_values))
    try:
        connexion.commit()
        print(f"L'utilisateur 'Unassigned Element' a été créé.")
    except mysql.connector.Error as err:
        connexion.rollback()
        print(f"Erreur lors de la transaction. Annulation des modifications : {err}")
        return False
    return True


def create_roles(cursor, connexion):
    # Définition des rôles et de leur statut is_superuser
    roles = permission_manager.get_roles_and_su_permission()

    if roles:
        for role in roles:
            query = "INSERT INTO roles (name, is_superuser) VALUES (%s, %s)"
            cursor.execute(query, role)
            try:
                connexion.commit()
                print(f"Le rôle {role[0]} a été créé.")
            except mysql.connector.Error as err:
                connexion.rollback()
                print(
                    f"Erreur lors de la transaction. Annulation des modifications : {err}"
                )
        return roles


def create_permissions(cursor, connexion):
    # Définition des rôles et de leur statut is_superuser
    permissions = permission_manager.get_permissions_and_description()

    if permissions:
        for permission in permissions:
            query = "INSERT INTO permissions (name, description) VALUES (%s, %s)"
            cursor.execute(query, permission)
            try:
                connexion.commit()
                print(f"La permission {permission[0]} a été créée.")
            except mysql.connector.Error as err:
                connexion.rollback()
                print(
                    f"Erreur lors de la transaction. Annulation des modifications : {err}"
                )
        return permissions


def assign_permissions_to_roles(cursor, connexion):
    """
    Attribue les permissions aux rôles dans la base de données en utilisant des requêtes SQL brutes.
    """
    print("Attribution des Permissions aux Rôles ...")

    # 1. Récupérer les IDs des rôles
    roles_id_map = {}
    try:
        cursor.execute("SELECT id, name FROM roles")
        for role_id, role_name in cursor.fetchall():
            roles_id_map[role_name] = role_id
    except mysql.connector.Error as err:
        print(f"Erreur lors de la récupération des rôles : {err}")
        return False

    # 2. Récupérer les IDs des permissions
    permissions_id_map = {}
    try:
        cursor.execute("SELECT id, name FROM permissions")
        for perm_id, perm_name in cursor.fetchall():
            permissions_id_map[perm_name] = perm_id
    except mysql.connector.Error as err:
        print(f"Erreur lors de la récupération des permissions : {err}")
        return False

    # 3. Définir les attributions (rôle -> liste de noms de permissions)
    role_permissions_mapping = {
        "collaborateur": ["read:client", "read:contract", "read:event"],
        "gestion": [
            "create:user",
            "update:user",
            "delete:user",
            "update:client",
            "create:contract",
            "update:contract",
            "update:event",
        ],
        "commercial": [
            "create:client",
            "update:client",
            "update:contract",
            "create:event",
        ],
        "support": ["update:event"],
    }

    # 4. Insérer les liens dans la table d'association role_permission
    for role_name, perm_names_list in role_permissions_mapping.items():
        role_id = roles_id_map.get(role_name)
        if role_id is None:
            print(f"Avertissement : Rôle '{role_name}' introuvable dans la DB. Ignoré.")
            continue

        for perm_name in perm_names_list:
            permission_id = permissions_id_map.get(perm_name)
            if permission_id is None:
                print(
                    f"Avertissement : Permission '{perm_name}' introuvable dans la DB. Ignorée pour le rôle '{role_name}'."
                )
                continue

            try:
                # Vérifier si l'association existe déjà pour éviter les duplicatas (si la PK n'est pas composée des deux ID)
                # Si (role_id, permission_id) est une clé primaire composée, l'INSERT provoquerait l'erreur 1062
                insert_query = "INSERT INTO role_permission (role_id, permission_id) VALUES (%s, %s)"
                cursor.execute(insert_query, (role_id, permission_id))
                connexion.commit()
                print(f"Lien créé : Rôle '{role_name}' -> Permission '{perm_name}'.")
            except mysql.connector.Error as err:
                connexion.rollback()
                # Gérer spécifiquement l'erreur de doublon si nécessaire (ER_DUP_ENTRY)
                if err.errno == 1062:
                    print(f"Lien '{role_name}' -> '{perm_name}' existe déjà. Ignoré.")
                else:
                    print(
                        f"Erreur lors de la création du lien {role_name} -> {perm_name} : {err}"
                    )
    print("Attribution des permissions aux rôles terminée.")
