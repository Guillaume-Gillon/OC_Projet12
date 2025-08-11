from Model.tables import Contract
from Model import db_manager
from View import data_collect, menu
from View.display_messages import display_message
from Controller import global_manager
from Controller.permission_manager import permission_required

import uuid
import sentry_sdk


def decode_contract_id(contract):
    return uuid.UUID(bytes=contract.id)


@permission_required("create:contract")
def create_contract(session):
    clients_instances = db_manager.load_clients_list(session)
    if not clients_instances:
        return None
    client_id = menu.client_list_menu(clients_instances)
    if not client_id:
        return None
    contract_data = data_collect.new_contract_data()
    question = "Le contrat est-il signé ?"
    if menu.menu_yes_no(question):
        contract_data["signed"] = True

    client = db_manager.load_clients_list(session, client_id)
    if client:
        contract_data["client"] = client
        contract_data["commercial_contact"] = client.commercial_contact

    new_contract = Contract(**contract_data)
    session.add(new_contract)
    if db_manager.commit_changes_to_db(session):
        if new_contract.signed:
            new_contract_id = decode_contract_id(new_contract)
            sentry_sdk.capture_message(
                f"Le contrat n°{new_contract_id} a été signé.",
                level="info",
            )
        return new_contract
    return None


@permission_required("update:contract")
def modify_contract(session, user):

    contracts_instances = None

    for role in user.roles:
        if role.name == "gestion":
            contracts_instances = db_manager.load_contracts_list(session)
            break

    if not contracts_instances:
        affected_contracts = db_manager.load_contracts_affected_to_user(session, user)
        if affected_contracts:
            contracts_instances = affected_contracts
        else:
            display_message("Aucun contrat modifiable n'a été trouvé !")
            return False

    contract_id = menu.contract_list_menu(contracts_instances)

    if not contract_id:
        return False

    for contract_instance in contracts_instances:
        if contract_instance.id == contract_id:
            contract = contract_instance
            break

    fields = {
        "amount": "Montant total",
        "balance_due": "Reste à payer",
        "signed": "Etat (signé / non-signé)",
        "client": "Client associé au contrat",
        "commercial_contact": "Commercial Epic Events associé au contrat",
    }

    selected_field, selected_key = global_manager.select_field(fields)
    if not selected_key:
        return False

    elif selected_key not in ["signed", "client", "commercial_contact"]:
        valid_new_data = False
        while not valid_new_data:
            new_data = data_collect.modify_contract_data(selected_key)
            try:
                int(new_data)
                valid_new_data = True
            except ValueError:
                print("Vous devez entrer un nombre entier !")

        new_data_list = [new_data]
        if not global_manager.confirm_new_data(selected_field, new_data_list):
            return False

        match selected_key:
            case "amount":
                contract.amount = new_data
            case "balance_due":
                contract.balance_due = new_data

    else:
        match selected_key:
            case "signed":
                if contract.signed:
                    contract_state = "Signé"
                else:
                    contract_state = "Non signé"
                contract_signed = menu.menu_yes_no(
                    f"Le contrat est-il signé ? (Etat actuel : {contract_state})"
                )
                if contract_signed:
                    contract_id = decode_contract_id(contract)
                    sentry_sdk.capture_message(
                        f"Le contrat n°{contract_id} a été signé.",
                        level="info",
                    )
                contract.signed = contract_signed

            case "client":
                clients = db_manager.load_clients_list(session)
                entries = [
                    f"{client.name} ({client.company_name})" for client in clients
                ]
                index_selected_client = menu.menu_select_client(entries)
                new_client = clients[index_selected_client]

                if new_client == contract.client:
                    display_message(
                        "Le client sélectionné est déjà le client enregistré pour ce contrat !"
                    )
                    return False
                contract.client = new_client

            case "commercial_contact":
                new_commercial_contact = global_manager.new_contact(
                    session,
                    "CONTACT COMMERCIAL",
                    "commercial",
                    contract.commercial_contact,
                )

                if not new_commercial_contact:
                    if new_commercial_contact is None:
                        display_message(
                            "Aucun collaborateur n'est assignable à ce contrat."
                        )
                    return False

                if new_commercial_contact == contract.commercial_contact:
                    display_message(
                        "L'utilisateur sélectionné est déjà le contact commercial pour ce contrat !"
                    )
                    return False

                new_data = [
                    new_commercial_contact.first_name,
                    new_commercial_contact.last_name,
                ]
                if not global_manager.confirm_new_data(selected_field, new_data):
                    return False

                contract.commercial_contact = new_commercial_contact

    if db_manager.commit_changes_to_db(session):
        return True

    return False


@permission_required("read:contract")
def filter_contracts(session, user):
    menu_options = []
    for role in user.roles:
        match role.name:
            case "gestion":
                menu_options.append("Afficher les contrats sans contact commercial")

            case "commercial":
                menu_options.append("Afficher les contrats à signer")
                menu_options.append("Afficher les contrats non soldés")
                menu_options.append("Afficher les contrats qui me sont attribués")

    selected_option = menu.menu_filter_elements(menu_options)
    match selected_option:

        case "Afficher les contrats sans contact commercial":
            contracts = db_manager.load_contracts_without_commercial(session)
            if not contracts:
                display_message("Aucun élément à afficher.")
                return None
            return contracts

        case "Afficher les contrats à signer":
            contracts = db_manager.load_contracts_to_sign(session)
            if not contracts:
                display_message("Aucun élément à afficher.")
                return None
            return contracts

        case "Afficher les contrats non soldés":
            contracts = db_manager.load_contract_to_sold(session)
            if not contracts:
                display_message("Aucun élément à afficher.")
                return None
            return contracts

        case "Afficher les contrats qui me sont attribués":
            contracts = db_manager.load_contracts_affected_to_user(session, user)
            if not contracts:
                display_message("Aucun élément à afficher.")
                return None
            return contracts

        case menu.DISPLAY_ALL:
            contracts = db_manager.load_contracts_list(session)
            if not contracts:
                display_message("Aucun élément à afficher.")
                return None
            return contracts

    return None
