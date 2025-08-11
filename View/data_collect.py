from View import menu
from Controller import password_manager, global_manager


from typing import Dict
from prompt_toolkit import prompt
import getpass

# --- DONNEES UTILISATEUR ---


def user_connection_data():
    employee_number = input("Entrez votre numéro employé ('Q' pour quitter) : ")
    if employee_number == "Q":
        return None, None
    employee_password = getpass.getpass("Entrez votre mot de passe : ")
    return employee_number, employee_password


def get_actual_password():
    return getpass.getpass("Entrez votre mot de passe actuel (tapez 0 pour annuler) : ")


def new_user_data(session) -> Dict:
    print("CREATION D'UN NOUVEL UTILISATEUR")
    user_data = {}
    user_data["employee_number"] = employee_number_entry(
        session, "Entrez le numéro employé du nouveau collaborateur : "
    )
    user_data["first_name"] = input("Entrez son prénom : ")
    user_data["last_name"] = input("Entrez son nom : ")
    user_data["email"] = email_entry(session, "Entrez son adresse e-mail : ")
    user_data["roles"] = menu.menu_define_role_to_user()
    user_data["password"] = password_manager.password_validation()
    return user_data


def modify_user_data(session, entry):
    if entry == "email":
        data = email_entry(session, "Entrez l'adresse e-mail du collaborateur' : ")
    else:
        data = None
    return data


def employee_number_entry(session, message):
    valid_number = False
    while not valid_number:
        employee_number = input(message)
        valid_number = global_manager.valid_employee_number(session, employee_number)
        if not valid_number:
            print("Ce numéro employé est déjà attribué !")
    return employee_number


def email_entry(session, message):
    email_validation = False
    while not email_validation:
        email = input(message)
        email_validation = global_manager.valid_email(session, email)
    return email


# --- DONNEES CLIENT ---


def new_client_data() -> Dict:
    print("CREATION D'UN NOUVEAU CLIENT")
    client_data = {}
    client_data["name"] = input("Entrez le nom complet du contact (prénom/nom) : ")
    client_data["email"] = input("Entrez l'adresse e-mail du contact : ")
    client_data["phone_number"] = input("Entrez le numéro de téléphone du contact : ")
    client_data["company_name"] = input("Entrez le nom de l'entreprise cliente : ")
    return client_data


def modify_client_data(entry):
    if entry == "name":
        data = input("Entrez le nouveau nom du client : ")
    elif entry == "email":
        data = input("Entrez le nouvel e-mail du client : ")
    elif entry == "phone_number":
        data = input("Entrez le nouveau numéro de téléphone du client : ")
    elif entry == "company_name":
        data = input("Entrez le nouveau nom de l'entreprise du client : ")
    else:
        data = None
    return data


# --- DONNEES CONTRATS ---


def new_contract_data() -> Dict:
    print("CREATION D'UN NOUVEAU CONTRAT")

    contract_data = {}
    contract_data["amount"] = float_entry("Entrez le montant total du contrat : ")
    contract_data["balance_due"] = float_entry("Entrez le montant restant à payer : ")

    return contract_data


def modify_contract_data(entry):
    if entry == "amount":
        data = float_entry("Entrez le nouveau montant total du contrat : ")
    elif entry == "balance_due":
        data = float_entry("Entrez le nouveau montant restant à payer du contrat : ")
    else:
        data = None
    return data


def float_entry(message):
    valid_data_type = False
    while not valid_data_type:
        amount_user_entry = input(message)
        valid_data_type = global_manager.valid_float_user_entry(amount_user_entry)
    return float(amount_user_entry)


# --- DONNEES EVENEMENTS ---


def new_event_data() -> Dict:
    print("CREATION D'UN NOUVEL EVENEMENT")
    event_data = {}

    event_data["name"] = input("Entrez le nom de l'évènement : ")
    event_data["location"] = input("Entrez le lieu de l'évènement : ")
    event_data["start_at"] = date_entry("Entrez la date de début (JJ/MM/AAAA) : ")
    event_data["end_at"] = date_entry("Entrez la date de fin (JJ/MM/AAAA) : ")
    event_data["attendees"] = attendees_entry("Entrez le nombre d'invités : ")
    event_data["notes"] = input("Vous pouvez ajouter un mémo, une description : ")

    return event_data


def modify_event_data(entry, notes=None):
    if entry == "name":
        data = input("Entrez le nouveau nom de l'évènement : ")

    elif entry == "start_at":
        data = date_entry("Nouvelle date de début de l'évènement (JJ/MM/AAAA) : ")

    elif entry == "end_at":
        data = date_entry("Nouvelle date de fin de l'évènement (JJ/MM/AAAA) : ")

    elif entry == "location":
        data = input("Entrez le nouveau lieu de l'évènement : ")

    elif entry == "attendees":
        data = attendees_entry("Entrez le nouveau nombre d'invités à l'évènement : ")

    elif entry == "notes":
        data = prompt(
            "Tapez Alt+Entrée pour valider :\n",
            default=notes,
            multiline=True,
        )

    else:
        data = None
    return data


def date_entry(message):
    valid_date = None
    while not valid_date:
        date = input(message)
        valid_format_date = global_manager.date_format_validation(date)
        if valid_format_date:
            valid_date = global_manager.date_not_in_past(valid_format_date)
    return valid_format_date


def attendees_entry(message):
    valid_int_number = False
    while not valid_int_number:
        int_number = input(message)
        valid_int_number = global_manager.valid_integer(int_number)
    return int(int_number)
