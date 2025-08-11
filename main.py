from View import menu, display_tables
from View.display_messages import display_message
from Model import db_manager
from Controller import (
    session_manager,
    user_manager,
    jwt_manager,
    client_manager,
    contract_manager,
    event_manager,
)

import sentry_sdk
from dotenv import load_dotenv
import os

load_dotenv("Config/sentry_config.env")
SENTRY_DSN = os.getenv("SENTRY_DSN")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    send_default_pii=True,
)

QUIT = "Quitter"


def run_create_user(session):
    user = user_manager.create_user(None, session)
    if user:
        display_message(
            f"L'utilisateur {user.first_name} {user.last_name} a été créé avec succès !"
        )
        return user
    display_message("Une erreur s'est produite. Fermeture du programme...")
    return QUIT


def run_connection_menu(session):
    user_choice = menu.landing_menu()
    match user_choice:
        case "Se connecter":
            if not user_manager.usertable_contains_data(session):
                print("Aucun utilisateur n'a été trouvé dans la base.")
                run_create_user(session)
                return run_connection_menu(session)
        case "Quitter":
            return QUIT


def to_main_menu(user):
    return user


def run(session, user=None):
    valid_token, decoded_payload, token = jwt_manager.load_jwt()

    if valid_token:
        user = user_manager.get_user_from_jwt(session, decoded_payload, token)
    else:
        if user:
            print("Session déconnectée.")
            return QUIT

    if not user:
        user = user_manager.connect_user(session)

    token = user_manager.update_jwt(user, session)

    if user:
        main_menu = menu.main_menu(user.roles, user.first_name, user.last_name)

        match main_menu:
            case "Espace personnel":
                user_account_menu = menu.user_account_menu(
                    user.roles, user.first_name, user.last_name
                )

                match user_account_menu:
                    case "Modifier mon mot de passe":
                        if user_manager.modify_user_password(user):
                            if not db_manager.commit_changes_to_db(session):
                                return QUIT
                            display_message("Le mot de passe a bien été modifié.")
                        return to_main_menu(user)

                    case "Déconnecter la session":
                        user.jwt_hash = ""
                        db_manager.commit_changes_to_db(session)
                        jwt_manager.delete_jwt_token_from_password_manager()
                        return QUIT

                    case "Menu principal":
                        return to_main_menu(user)

            case "Clients":
                client_menu = menu.client_menu(
                    user.roles, user.first_name, user.last_name
                )
                match client_menu:
                    case "Créer un nouveau client":
                        new_client = client_manager.create_client(token, session, user)
                        if new_client:
                            display_message(
                                f"Client créé : {new_client.name} - {new_client.company_name}"
                            )
                        return to_main_menu(user)

                    case "Modifier un client":
                        if client_manager.modify_client(token, session, user):
                            display_message("Modification enregistrée !")
                        return to_main_menu(user)

                    case "Afficher les clients":
                        clients_instances = client_manager.filter_clients(
                            token, session, user
                        )
                        if clients_instances:
                            display_tables.clients_table(clients_instances)
                        return to_main_menu(user)

                    case "Menu principal":
                        return to_main_menu(user)

            case "Contrats":
                contract_menu = menu.contract_menu(
                    user.roles, user.first_name, user.last_name
                )
                match contract_menu:
                    case "Créer un nouveau contrat":
                        contract = contract_manager.create_contract(token, session)
                        if contract:
                            decoded_uuid = contract_manager.decode_contract_id(contract)
                            display_message(
                                f"Contrat n°{decoded_uuid} créé avec succès !"
                            )
                        return to_main_menu(user)

                    case "Modifier un contrat":
                        if contract_manager.modify_contract(token, session, user):
                            display_message("Modification enregistrée !")
                        return to_main_menu(user)

                    case "Afficher les contrats":
                        contracts_instances = contract_manager.filter_contracts(
                            token, session, user
                        )
                        if contracts_instances:
                            display_tables.contracts_table(contracts_instances)
                        return to_main_menu(user)

                    case "Menu principal":
                        return to_main_menu(user)

            case "Evènements":
                event_menu = menu.event_menu(
                    user.roles, user.first_name, user.last_name
                )
                match event_menu:
                    case "Créer un nouvel évènement":
                        new_event = event_manager.create_event(token, session)
                        if new_event:
                            display_message(
                                f"L'évènement '{new_event.name}' a été enregistré avec succès !"
                            )
                        return to_main_menu(user)

                    case "Modifier un évènement":
                        if event_manager.modify_event(token, session, user):
                            display_message("Modification enregistrée !")
                        return to_main_menu(user)

                    case "Afficher les évènements":
                        events_instances = event_manager.filter_events(
                            token, session, user
                        )
                        if events_instances:
                            display_tables.events_table(events_instances)
                        return to_main_menu(user)

                    case "Menu principal":
                        return to_main_menu(user)

            case "Collaborateurs":
                user_menu = menu.user_menu(user.roles, user.first_name, user.last_name)
                match user_menu:
                    case "Créer un nouveau collaborateur":
                        new_user = user_manager.create_user(token, session)
                        if new_user:
                            display_message(
                                f"L'utilisateur {new_user.first_name} {new_user.last_name} a été créé avec succès !"
                            )
                        return to_main_menu(user)

                    case "Modifier les informations d'un collaborateur":
                        if user_manager.modify_user(token, session, user):
                            display_message("Modifications effectuées avec succès !")
                        return to_main_menu(user)

                    case "Supprimer un collaborateur":
                        if user_manager.delete_user(token, session, user):
                            display_message("Modifications effectuées avec succès !")
                        return to_main_menu(user)

            case "Quitter":
                return QUIT
    else:
        print("Une erreur s'est produite.")
        return QUIT


def verify_data(data):
    if data == QUIT:
        session_manager.disconnect_app_from_db(session, engine)
        exit()


session, engine = session_manager.connect_app_to_db()
if not session:
    exit()
data = run_connection_menu(session)
verify_data(data)
while True:
    data = run(session, user=data)
    verify_data(data)
