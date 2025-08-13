from Model import db_manager
from View import menu

import datetime


def new_contact(session, contact_department, role, actual_contact):
    users = db_manager.load_users_by_role(session, role)
    if users:
        entries = [f"{user.first_name} {user.last_name}" for user in users]
        index_selected_user = menu.menu_select_department_user(
            entries, contact_department, actual_contact
        )
        if not index_selected_user:
            if index_selected_user is None:
                return None
            return False
        new_contact = users[index_selected_user - 1]
        return new_contact
    return None


def confirm_new_data(selected_field, data):
    new_data = ""
    for element in data:
        new_data += str(element) + " "
    return menu.menu_yes_no(
        f"{selected_field} -> {new_data}: Confirmer la modification ?"
    )


def select_field(fields):
    menu_options = list(fields.values())
    selected_field = menu.menu_class_fields(menu_options)
    if not selected_field:
        return None, None

    for key, value in fields.items():
        if value == selected_field:
            selected_key = key
            return selected_field, selected_key
    return None, None


def load_role_names(roles):
    role_names = []
    for role in roles:
        if role.name == "collaborateur":
            if len(roles) > 1:
                continue
        role_names.append(role.name)
    return role_names


def date_format_for_display(date):
    return date.strftime("%d/%m/%Y")


# --- VALIDATIONS ---


def valid_float_user_entry(entry):
    try:
        float(entry)
        return True
    except ValueError:
        print("Erreur : La saisie n'est pas un nombre décimal valide.")
        return False


def date_format_validation(date):
    try:
        format = "%d/%m/%Y"
        date_obj = datetime.datetime.strptime(date, format)
        return date_obj

    except ValueError:
        print("ERREUR : Veuillez utiliser le format JJ/MM/AAAA.")
        print()
        return None


def date_not_in_past(input_date):
    date_to_compare = input_date.date()
    if date_to_compare < datetime.date.today():
        print("ERREUR : Cette date est déjà passée.")
        print()
        return False
    return True


def valid_integer(entry):
    try:
        int(entry)
        return True
    except ValueError:
        print("Erreur : La saisie n'est pas un nombre entier valide.")
        return False


def valid_employee_number(session, employee_number):
    if db_manager.load_users_by_employee_number(session, employee_number):
        return False
    return True


def valid_email(session, email):
    if db_manager.load_users_by_email(session, email):
        return False
    return True
