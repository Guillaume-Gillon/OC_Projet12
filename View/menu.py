from Controller import global_manager

from simple_term_menu import TerminalMenu

ADD_MENU_ENTRY_INDEX = -1
DISPLAY_ALL = "Afficher tous les éléments"
DEBUG = False


# MENU DE CONNEXION
def landing_menu():
    menu_options = ["Se connecter", "Quitter"]
    menu_title = "EPIC EVENTS CRM"
    selected_option = load_menu(menu_options, menu_title)
    return menu_options[selected_option]


# MENU PRINCIPAL
def main_menu(roles, first_name, last_name):

    role_names = global_manager.load_role_names(roles)
    menu_title = define_menu_title("MENU PRINCIPAL", role_names, first_name, last_name)
    menu_options = [
        "Espace personnel",
        "Clients",
        "Contrats",
        "Evènements",
        "Quitter",
    ]

    index = 1
    for role in roles:
        if role == "collaborateur":
            continue
        else:
            for permission in role.permissions:
                if permission.name in ["create:user", "update:user", "delete:user"]:
                    menu_options.insert(index, "Collaborateurs")
                    break

    selected_option = load_menu(menu_options, menu_title)
    return menu_options[selected_option]


# --- MENUS UTILISATEUR ---


def user_account_menu(roles, first_name, last_name):
    role_names = global_manager.load_role_names(roles)
    menu_title = define_menu_title(
        "ESPACE PERSONNEL", role_names, first_name, last_name
    )
    menu_options = [
        "Modifier mon mot de passe",
        "Déconnecter la session",
        "Menu principal",
    ]
    selected_option = load_menu(menu_options, menu_title)
    return menu_options[selected_option]


def user_menu(roles, first_name, last_name):
    role_names = global_manager.load_role_names(roles)
    menu_title = define_menu_title(
        "MENU UTILISATEURS", role_names, first_name, last_name
    )
    menu_options = []
    for role in roles:
        for permission in role.permissions:
            match permission.name:
                case "create:user":
                    if "Créer un nouveau collaborateur" not in menu_options:
                        menu_options.insert(
                            ADD_MENU_ENTRY_INDEX, "Créer un nouveau collaborateur"
                        )
                case "update:user":
                    if (
                        "Modifier les informations d'un collaborateur"
                        not in menu_options
                    ):
                        menu_options.insert(
                            ADD_MENU_ENTRY_INDEX,
                            "Modifier les informations d'un collaborateur",
                        )
                case "delete:user":
                    if "Supprimer un collaborateur" not in menu_options:
                        menu_options.insert(
                            ADD_MENU_ENTRY_INDEX, "Supprimer un collaborateur"
                        )

    menu_options.sort()
    menu_options.append("Menu principal")

    selected_option = load_menu(menu_options, menu_title)
    return menu_options[selected_option]


def user_list_menu(users_instances):
    menu_title = "LISTE DES COLLABORATEURS ENREGISTRES"
    users_to_display = [
        user for user in users_instances if not user.first_name == "Unassigned"
    ]
    id = get_id_from_selected_option(menu_title, users_to_display)
    if id:
        return id
    return None


def menu_define_role_to_user(role_affected=None):
    menu_title = "ENTREZ LE ROLE DU COLLABORATEUR"
    roles_options = ["commercial", "gestion", "support"]
    if role_affected:
        for role in role_affected:
            roles_options.remove(role)
        roles_options.append("Retour")

    if roles_options:
        roles_menu = TerminalMenu(roles_options, title=menu_title)
        selected_index = roles_menu.show()
        if roles_options[selected_index] == "Retour":
            return False
        return roles_options[selected_index]
    return None


def menu_remove_role_to_user(roles_options):
    if not roles_options:
        return None
    else:
        roles_options.append("Retour")

    menu_title = "ENTREZ LE ROLE A SUPPRIMER"
    roles_menu = TerminalMenu(roles_options, title=menu_title)
    selected_index = roles_menu.show()
    if roles_options[selected_index] == "Retour":
        return False
    return roles_options[selected_index]


def menu_select_department_user(entries, contact_department, actual_contact):
    if actual_contact:
        menu_title = f"SELECTIONNEZ LE NOM DU NOUVEAU {contact_department} (Contact actuel : {actual_contact.first_name} {actual_contact.last_name})"
    else:
        menu_title = f"SELECTIONNEZ LE NOM DU NOUVEAU {contact_department} (Contact actuel : Aucun)"
    entries.insert(0, "Retour")
    selected_entry = load_menu(entries, menu_title)
    if selected_entry == "Retour":
        return False
    return selected_entry


# --- MENUS CLIENTS ---


def client_menu(roles, first_name, last_name):
    role_names = global_manager.load_role_names(roles)
    menu_title = define_menu_title("MENU CLIENT", role_names, first_name, last_name)
    menu_options = []
    for role in roles:
        for permission in role.permissions:
            match permission.name:
                case "read:client":
                    menu_options.insert(ADD_MENU_ENTRY_INDEX, "Afficher les clients")
                case "create:client":
                    if "Créer un nouveau client" not in menu_options:
                        menu_options.insert(
                            ADD_MENU_ENTRY_INDEX, "Créer un nouveau client"
                        )
                case "update:client":
                    if "Modifier un client" not in menu_options:
                        menu_options.insert(ADD_MENU_ENTRY_INDEX, "Modifier un client")

    menu_options.sort()
    menu_options.append("Menu principal")

    selected_option = load_menu(menu_options, menu_title)
    return menu_options[selected_option]


def client_list_menu(clients_instances):
    menu_title = "LISTE DES CLIENTS ENREGISTRES"
    id = get_id_from_selected_option(menu_title, clients_instances)
    if id:
        return id
    return None


def menu_select_client(entries):
    menu_title = "SELECTIONNEZ LE NOM DU NOUVEAU CLIENT"
    return load_menu(entries, menu_title)


# --- MENUS CONTRATS ---


def contract_menu(roles, first_name, last_name):
    role_names = global_manager.load_role_names(roles)
    menu_title = define_menu_title("MENU CONTRATS", role_names, first_name, last_name)
    menu_options = []
    for role in roles:
        for permission in role.permissions:
            match permission.name:
                case "read:contract":
                    menu_options.insert(ADD_MENU_ENTRY_INDEX, "Afficher les contrats")
                case "create:contract":
                    if "Créer un nouveau contrat" not in menu_options:
                        menu_options.insert(
                            ADD_MENU_ENTRY_INDEX, "Créer un nouveau contrat"
                        )
                case "update:contract":
                    if "Modifier un contrat" not in menu_options:
                        menu_options.insert(ADD_MENU_ENTRY_INDEX, "Modifier un contrat")

    menu_options.sort()
    menu_options.append("Menu principal")

    selected_option = load_menu(menu_options, menu_title)
    return menu_options[selected_option]


def contract_list_menu(contracts_instances):
    menu_title = "LISTE DES CONTRATS ENREGISTRES"
    id = get_id_from_selected_option(menu_title, contracts_instances)
    if id:
        return id
    return None


# --- MENUS EVENEMENTS ---


def event_menu(roles, first_name, last_name):
    role_names = global_manager.load_role_names(roles)
    menu_title = define_menu_title("MENU EVENEMENTS", role_names, first_name, last_name)
    menu_options = []
    for role in roles:
        for permission in role.permissions:
            match permission.name:
                case "read:event":
                    menu_options.insert(ADD_MENU_ENTRY_INDEX, "Afficher les évènements")
                case "create:event":
                    if "Créer un nouvel évènement" not in menu_options:
                        menu_options.insert(
                            ADD_MENU_ENTRY_INDEX, "Créer un nouvel évènement"
                        )
                case "update:event":
                    if "Modifier un évènement" not in menu_options:
                        menu_options.insert(
                            ADD_MENU_ENTRY_INDEX, "Modifier un évènement"
                        )

    menu_options.sort()
    menu_options.append("Menu principal")

    selected_option = load_menu(menu_options, menu_title)
    return menu_options[selected_option]


def event_list_menu(events_instances):
    menu_title = "LISTE DES EVENEMENTS ENREGISTRES"
    id = get_id_from_selected_option(menu_title, events_instances)
    if id:
        return id
    return None


# --- DIVERS ---


def define_menu_title(type, role_names, first_name, last_name):
    role_names_upper = [name.upper() for name in role_names]
    roles_str = " - ".join(role_names_upper)
    menu_title = f"EPIC EVENTS CRM - {type} - {first_name.upper()} {last_name.upper()} ({roles_str})"
    return menu_title


def load_menu(menu_options, menu_title):
    if DEBUG:
        menu = TerminalMenu(menu_options, title=menu_title)
    else:
        menu = TerminalMenu(menu_options, title=menu_title, clear_screen=True)
    return menu.show()


def get_id_from_selected_option(menu_title, instances):
    instances_map = {str(instance): instance for instance in instances}
    menu_options = [str(instance) for instance in instances]
    menu_options.insert(0, "Retour")

    index = load_menu(menu_options, menu_title)
    selected_option = menu_options[index]
    if selected_option == "Retour":
        return None
    selected_instance = instances_map[selected_option]
    return selected_instance.id


def menu_yes_no(question):
    menu_options = ["Oui", "Non"]
    menu = TerminalMenu(menu_options, title=question)
    selected_option = menu.show()
    if menu_options[selected_option] == "Oui":
        return True
    return False


def menu_class_fields(menu_options):
    menu_title = "QUEL CHAMP SOUHAITEZ-VOUS MODIFIER ?"
    menu_options.append("Menu principal")
    selected_option = load_menu(menu_options, menu_title)
    if menu_options[selected_option] == "Menu principal":
        return None
    return menu_options[selected_option]


def menu_filter_elements(menu_options):
    menu_title = "FILTRAGE DES ELEMENTS A AFFICHER"
    additional_menu_entries = [DISPLAY_ALL, "Menu Principal"]
    for entry in additional_menu_entries:
        menu_options.append(entry)
    selected_option = load_menu(menu_options, menu_title)
    if menu_options[selected_option] == "Menu principal":
        return None
    return menu_options[selected_option]
