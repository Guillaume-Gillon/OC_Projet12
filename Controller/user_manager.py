from Model.tables import User
from Model import db_manager
from View import data_collect, menu
from View.display_messages import display_message
from Controller import password_hasher, password_manager, jwt_manager, global_manager
from Controller.permission_manager import permission_required

import sentry_sdk


def usertable_contains_data(session):
    users = db_manager.load_all_users(session)
    if users:
        for user in users:
            if user.first_name == "Unassigned":
                users.remove(user)
                if len(users) > 0:
                    return True
    return False


def connect_user(session):
    print("EPIC EVENTS CRM - CONNEXION")
    user_found = False
    while not user_found:
        employee_number, user_password = data_collect.user_connection_data()
        if not employee_number:
            return None
        user = db_manager.load_users_by_employee_number(session, employee_number)
        if not user:
            print("Le numéro ne correspond à aucun utilisateur enregistré.")
        else:
            if password_hasher.verify_password(user.password_hash, user_password):
                user_found = True
                return user


# --- CRUD UTILISATEURS ---


def create_user(auth_token, session):
    if not usertable_contains_data(session):
        return user_data(session)

    if not auth_token:
        display_message("Permission refusée : Jeton d'identification manquant.")
        return None
    else:
        payload = jwt_manager.decode_jwt(auth_token)
        if payload:
            user_permissions = payload.get("permissions", [])
            if "create:user" in user_permissions:
                return user_data(session)
            else:
                display_message("Accès refusé.")
        else:
            display_message("Accès refusé.")
    return None


def user_data(session):
    user_data = data_collect.new_user_data(session)
    hashed_password = password_hasher.hash_password(user_data["password"])
    if hashed_password:
        user_data["password_hash"] = hashed_password
        del user_data["password"]

    user_asked_role = user_data["roles"]
    default_role = db_manager.load_role(session, "collaborateur")
    role_obj = db_manager.load_role(session, user_asked_role)
    user_data["roles"] = [role_obj]
    user_data["roles"].append(default_role)

    new_user = User(**user_data)
    session.add(new_user)
    if db_manager.commit_changes_to_db(session):
        session.refresh(new_user)
        sentry_sdk.capture_message(
            f"L'utilisateur {new_user.first_name} {new_user.last_name} a été créé.",
            level="info",
        )
        return new_user


@permission_required("update:user")
def modify_user(session, actual_user):

    users_instances = db_manager.load_all_users(session)
    user_id = menu.user_list_menu(users_instances)
    if not user_id:
        return False
    for user_instance in users_instances:
        if user_instance.id == user_id:
            user = user_instance
            break

    fields = {
        "email": "Adresse e-mail",
        "add_role": "Affecter un rôle",
        "remove_role": "Désaffecter un rôle",
    }

    selected_field, selected_key = global_manager.select_field(fields)
    if not selected_key:
        return False

    elif selected_key not in ["add_role", "remove_role"]:
        new_data = data_collect.modify_user_data(session, selected_key)

        new_data_list = [new_data]
        if not global_manager.confirm_new_data(selected_field, new_data_list):
            return False

        match selected_key:
            case "email":
                user.email = new_data

    else:
        match selected_key:
            case "add_role":
                roles_affected = []
                for role in user.roles:
                    if role.name == "collaborateur":
                        continue
                    roles_affected.append(role.name)
                new_role = menu.menu_define_role_to_user(roles_affected)

                if new_role is None:
                    display_message("Aucun rôle n'est disponible !")
                    return False
                elif new_role is False:
                    return False

                for role in user.roles:
                    if new_role == role.name:
                        display_message(
                            f"Le rôle sélectionné est déjà affecté à {user.first_name} {user.last_name} !"
                        )
                        return False

                new_role_instance = db_manager.load_role(session, new_role)
                user.roles.append(new_role_instance)

            case "remove_role":
                if len(user.roles) <= 2:
                    display_message(
                        "Vous devez affecter un nouveau rôle avant d'effectuer cette action."
                    )
                    return False

                else:
                    role_names = []
                    for role in user.roles:
                        if role.name == "collaborateur":
                            continue
                        role_names.append(role.name)
                    role_name_to_remove = menu.menu_remove_role_to_user(role_names)

                    if role_name_to_remove is None:
                        display_message("Aucun rôle n'est disponible !")
                        return False
                    elif role_name_to_remove is False:
                        return False
                    elif role_name_to_remove == "gestion" and user == actual_user:
                        if not menu.menu_yes_no(
                            "ATTENTION : Vous ne pourrez plus gérer les rôles des utilisateurs. Continuer ?"
                        ):
                            return False

                    role_name = [role_name_to_remove]
                    if verify_attached_elements(user, role_name):
                        if not attach_elements_to_unassigned_user(
                            session, user, list(role_name)
                        ):
                            return False

                    for role in user.roles:
                        if role_name_to_remove == role.name:
                            role_to_remove = db_manager.load_role(
                                session, role_name_to_remove
                            )
                            user.roles.remove(role_to_remove)

    if db_manager.commit_changes_to_db(session):
        if user == actual_user:
            if selected_key == "add_role" or selected_key == "remove_role":
                update_jwt(user, session)
            session.refresh(actual_user)
        if selected_key == "add_role" or selected_key == "remove_role":
            field = "role"
        else:
            field = selected_key
        sentry_sdk.capture_message(
            f"Le champ {field} de l'utilisateur "
            f"{user.first_name} {user.last_name} (ID : {user.id}) "
            f"a été modifié par {actual_user.first_name} {actual_user.last_name} (ID : {actual_user.id}).",
            level="info",
        )
        return True
    return False


@permission_required("delete:user")
def delete_user(session, actual_user):
    users_instances = db_manager.load_all_users(session)
    user_id = menu.user_list_menu(users_instances)
    if not user_id:
        return False
    for user_instance in users_instances:
        if user_instance.id == user_id:
            user = user_instance
            break

    if user == actual_user:
        display_message("Impossible de supprimer l'utilisateur actuel !")
        return False
    else:
        if menu.menu_yes_no(
            f"Supprimer l'utilisateur {user.first_name} {user.last_name} ?"
        ):
            roles_names = [role.name for role in user.roles]
            if verify_attached_elements(user, roles_names):
                if attach_elements_to_unassigned_user(session, user, roles_names):
                    session.delete(user)
                    if db_manager.commit_changes_to_db(session):
                        return True
    return False


def verify_attached_elements(user, role):
    data_found = False
    if "commercial" in role:
        if user.clients:
            print(f"Des clients sont assignés à {user.first_name} {user.last_name}")
            data_found = True
        if user.contracts:
            print(f"Des contrats sont assignés à {user.first_name} {user.last_name}")
            data_found = True
    if "support" in role:
        if user.events:
            print(f"Des évènements sont assignés à {user.first_name} {user.last_name}")
            data_found = True
    return data_found


def attach_elements_to_unassigned_user(session, user, role_names=[]):
    if menu.menu_yes_no(
        "Les éléments assignés vont être détachés de l'utilisateur sélectionné. Souhaitez-vous continuer ?"
    ):
        unassigned_user = db_manager.load_unassigned_user(session)
        role_unassigned = False
        if "commercial" in role_names:
            for client in user.clients:
                client.commercial_contact = unassigned_user
                role_unassigned = True
            for contract in user.contracts:
                contract.commercial_contact = unassigned_user
                role_unassigned = True
        if "support" in role_names:
            for event in user.events:
                event.support_contact = unassigned_user
                role_unassigned = True
        return role_unassigned
    return False


# --- GESTION DU PASSWORD ---


def modify_user_password(user):
    correct_password = False
    while not correct_password:
        user_input_password = data_collect.get_actual_password()
        if user_input_password == "0":
            return False
        if password_hasher.verify_password(user.password_hash, user_input_password):
            correct_password = True
    new_password = password_manager.password_validation()
    if new_password:
        hashed_new_password = password_hasher.hash_password(new_password)
        user.password_hash = hashed_new_password
        return True
    return False


def get_user_from_jwt(session, decoded_payload, token):
    user_id = int(decoded_payload.get("sub"))
    found_user = db_manager.load_user_by_id(session, user_id)
    if found_user:
        hashed_token = found_user.jwt_hash
        if password_hasher.verify_password(hashed_token, token):
            return found_user
    return None


def update_jwt(user, session):
    permissions = []
    for role in user.roles:
        for permission in role.permissions:
            permissions.append(permission.name)
    user_jwt = jwt_manager.create_jwt(user.id, permissions)
    if user_jwt:
        hashed_jwt = password_hasher.hash_password(user_jwt)
        user.jwt_hash = hashed_jwt
        db_manager.commit_changes_to_db(session)
        session.refresh(user)
        return user_jwt
