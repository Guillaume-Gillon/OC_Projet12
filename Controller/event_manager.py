from Model.tables import Event
from Model import db_manager
from View import data_collect, menu
from View.display_messages import display_message
from Controller import global_manager
from Controller.permission_manager import permission_required


@permission_required("create:event")
def create_event(session):

    contracts_instances = db_manager.load_contracts_list(session)
    contract_id = menu.contract_list_menu(contracts_instances)
    if not contract_id:
        return None
    for contract in contracts_instances:
        if contract.id == contract_id:
            contract_to_verify = contract
            break
    if not contract_to_verify.signed:
        display_message(
            "La création d'un évènement est impossible tant que le contrat n'est pas signé !"
        )
        return None
    event_data = data_collect.new_event_data()

    contract = db_manager.load_contracts_list(session, contract_id)
    if contract:
        event_data["contract"] = contract

    event_data["support_contact"] = None

    new_event = Event(**event_data)
    session.add(new_event)
    if db_manager.commit_changes_to_db(session):
        return new_event
    return None


@permission_required("update:event")
def modify_event(session, user):
    events_instances = None
    manager = False

    for role in user.roles:
        if role.name == "gestion":
            manager = True
            events_instances = db_manager.load_events_list(session)
            break

    if not events_instances:
        affected_events = db_manager.load_events_affected_to_user(session, user)

        if affected_events:
            events_instances = affected_events
        else:
            display_message("Aucun évènement modifiable n'a été trouvé !")
            return False

    event_id = menu.event_list_menu(events_instances)

    if not event_id:
        return False

    for event_instance in events_instances:
        if event_instance.id == event_id:
            event = event_instance
            break

    fields = {
        "name": "Nom de l'évènement",
        "start_at": "Date de début",
        "end_at": "Date de fin",
        "location": "Lieu de l'évènement",
        "attendees": "Nombre d'invités",
        "notes": "Notes",
    }

    if manager:
        fields["support_contact"] = "Contact support Epic Events"

    selected_field, selected_key = global_manager.select_field(fields)
    if not selected_key:
        return False

    elif selected_key not in ["support_contact"]:
        new_data = data_collect.modify_event_data(selected_key, event.notes)
        if selected_key == "start_at" or selected_key == "end_at":
            date_ready_to_save = new_data
            new_data = global_manager.date_format_for_display(new_data)

        new_data_list = [new_data]
        if not global_manager.confirm_new_data(selected_field, new_data_list):
            return False

        match selected_key:
            case "name":
                event.name = new_data
            case "start_at":
                event.start_at = date_ready_to_save
            case "end_at":
                event.start_at = date_ready_to_save
            case "location":
                event.location = new_data
            case "attendees":
                event.attendees = new_data
            case "notes":
                event.notes = new_data

    else:
        match selected_key:
            case "support_contact":
                new_support_contact = global_manager.new_contact(
                    session, "CONTACT SUPPORT", "support", event.support_contact
                )
                if not new_support_contact:
                    if new_support_contact is None:
                        display_message(
                            "Aucun collaborateur n'est assignable à cet évènement."
                        )
                    return False
                if new_support_contact == event.support_contact:
                    display_message(
                        "L'utilisateur sélectionné est déjà le contact de support pour cet évènement !"
                    )
                    return False

                new_data = [
                    new_support_contact.first_name,
                    new_support_contact.last_name,
                ]
                if not global_manager.confirm_new_data(selected_field, new_data):
                    return False

                event.support_contact = new_support_contact

    if db_manager.commit_changes_to_db(session):
        return True

    return False


@permission_required("read:event")
def filter_events(session, user):
    menu_options = []
    for role in user.roles:
        match role.name:
            case "gestion":
                menu_options.append("Afficher les évènements sans contact support")
            case "support":
                menu_options.append("Afficher les évènements qui me sont attribués")

    selected_option = menu.menu_filter_elements(menu_options)
    match selected_option:

        case "Afficher les évènements sans contact support":
            events = db_manager.load_events_without_support(session)
            if not events:
                display_message("Aucun élément à afficher.")
                return None
            return events

        case "Afficher les évènements qui me sont attribués":
            events = db_manager.load_events_affected_to_user(session, user)
            if not events:
                display_message("Aucun élément à afficher.")
                return None
            return events

        case menu.DISPLAY_ALL:
            events = db_manager.load_events_list(session)
            if not events:
                display_message("Aucun élément à afficher.")
                return None
            return events

    return None
