from Model.tables import Client
from Model import db_manager
from View import data_collect, menu
from View.display_messages import display_message
from Controller import global_manager
from Controller.permission_manager import permission_required


@permission_required("create:client")
def create_client(session, user):
    client_data = data_collect.new_client_data()
    client_data["commercial_contact"] = user

    new_client = Client(**client_data)
    session.add(new_client)
    if db_manager.commit_changes_to_db(session):
        return new_client
    return None


@permission_required("update:client")
def modify_client(session, user):

    clients_instances = None
    user_is_manager = True

    for role in user.roles:
        if role.name == "gestion":
            clients_instances = db_manager.load_clients_without_commercial(session)
        if role.name == "commercial":
            user_is_manager = False

    if not clients_instances:
        affected_clients = db_manager.load_clients_affected_to_user(session, user)
        if affected_clients:
            clients_instances = affected_clients
        else:
            display_message("Aucun client modifiable n'a été trouvé !")
            return False

    client_id = menu.client_list_menu(clients_instances)

    if not client_id:
        return False

    for client_instance in clients_instances:
        if client_instance.id == client_id:
            client = client_instance
            break

    fields = {
        "name": "Nom du client",
        "email": "Adresse e-mail du client",
        "phone_number": "Numéro de téléphone du client",
        "company_name": "Nom de l'entreprise du client",
        "commercial_contact": "Commercial Epic Events associé au client",
    }

    if user_is_manager:
        del fields["name"]
        del fields["email"]
        del fields["phone_number"]
        del fields["company_name"]

    selected_field, selected_key = global_manager.select_field(fields)
    if not selected_key:
        return False

    elif selected_key not in ["commercial_contact"]:
        new_data = data_collect.modify_client_data(selected_key)

        new_data_list = [new_data]
        if not global_manager.confirm_new_data(selected_field, new_data_list):
            return False

        match selected_key:
            case "name":
                client.name = new_data
            case "email":
                client.email = new_data
            case "phone_number":
                client.phone_number = new_data
            case "company_name":
                client.company_name = new_data

    else:
        match selected_key:
            case "commercial_contact":
                new_commercial_contact = global_manager.new_contact(
                    session,
                    "CONTACT COMMERCIAL",
                    "commercial",
                    client.commercial_contact,
                )

                if not new_commercial_contact:
                    if new_commercial_contact is None:
                        display_message(
                            "Aucun collaborateur n'est assignable à ce client."
                        )
                    return False

                if new_commercial_contact == client.commercial_contact:
                    display_message(
                        "L'utilisateur sélectionné est déjà le contact commercial pour ce client !"
                    )
                    return False

                new_data = [
                    new_commercial_contact.first_name,
                    new_commercial_contact.last_name,
                ]
                if not global_manager.confirm_new_data(selected_field, new_data):
                    return False

                client.commercial_contact = new_commercial_contact

    if db_manager.commit_changes_to_db(session):
        return True

    return False


@permission_required("read:client")
def filter_clients(session, user):
    menu_options = []
    for role in user.roles:
        match role.name:
            case "gestion":
                menu_options.append("Afficher les clients sans contact commercial")

            case "commercial":
                menu_options.append("Afficher les clients qui me sont attribués")

    selected_option = menu.menu_filter_elements(menu_options)
    match selected_option:

        case "Afficher les clients sans contact commercial":
            clients = db_manager.load_clients_without_commercial(session)
            if not clients:
                display_message("Aucun élément à afficher.")
                return None
            return clients

        case "Afficher les clients qui me sont attribués":
            clients = db_manager.load_clients_affected_to_user(session, user)
            if not clients:
                display_message("Aucun élément à afficher.")
                return None
            return clients

        case menu.DISPLAY_ALL:
            clients = db_manager.load_clients_list(session)
            if not clients:
                display_message("Aucun élément à afficher.")
                return None
            return clients

    return None
