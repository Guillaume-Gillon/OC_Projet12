from Model.tables import User, Role, Client, Contract, Event

import mysql.connector
from sqlalchemy import or_


def commit_changes_to_db(session):
    try:
        session.commit()
        return True
    except mysql.connector.Error as err:
        session.rollback()
        print(f"Erreur lors de la transaction. Annulation des modifications : {err}")
        return False


def load_role(session, asked_role):
    return session.query(Role).filter(Role.name == asked_role).first()


# --- REQUETES POUR UTILISATEUR ---


def load_all_users(session):
    return session.query(User).all()


def load_user_by_id(session, user_id):
    return session.query(User).filter(User.id == user_id).first()


def load_users_by_role(session, role):
    return session.query(User).join(User.roles).filter(Role.name == role).all()


def load_users_by_employee_number(session, employee_number):
    return session.query(User).filter(User.employee_number == employee_number).first()


def load_users_by_email(session, email):
    return session.query(User).filter(User.email == email).all()


def load_unassigned_user(session):
    return session.query(User).filter(User.first_name == "Unassigned").first()


# --- REQUETES POUR CLIENTS ---


def load_clients_list(session, client_id=None):
    if client_id:
        return session.query(Client).filter(Client.id == client_id).first()
    return session.query(Client).all()


def load_clients_without_commercial(session):
    unassigned_user = (
        session.query(User).filter(User.first_name == "Unassigned").first()
    )
    return (
        session.query(Client)
        .filter(
            or_(
                Client.commercial_contact is None,
                Client.commercial_contact == unassigned_user,
            )
        )
        .all()
    )


def load_clients_affected_to_user(session, user):
    return session.query(Client).filter(Client.commercial_contact == user).all()


# --- REQUETES POUR CONTRATS ---


def load_contracts_list(session, contract_id=None):
    if contract_id:
        try:
            contract_id_binary = contract_id.bytes
        except AttributeError:
            contract_id_binary = contract_id
        return session.query(Contract).filter(Contract.id == contract_id_binary).first()
    return session.query(Contract).all()


def load_contracts_affected_to_user(session, user):
    return session.query(Contract).filter(Contract.commercial_contact == user).all()


def load_contracts_without_commercial(session):
    unassigned_user = (
        session.query(User).filter(User.first_name == "Unassigned").first()
    )
    return (
        session.query(Contract)
        .filter(
            or_(
                Contract.commercial_contact is None,
                Contract.commercial_contact == unassigned_user,
            )
        )
        .all()
    )


def load_contracts_to_sign(session):
    return session.query(Contract).filter(Contract.signed is False).all()


def load_contract_to_sold(session):
    return session.query(Contract).filter(Contract.balance_due > 0).all()


# --- REQUETES POUR EVENEMENTS ---


def load_events_list(session):
    return session.query(Event).all()


def load_events_affected_to_user(session, user):
    return session.query(Event).filter(Event.support_contact == user).all()


def load_events_without_support(session):
    unassigned_user = (
        session.query(User).filter(User.first_name == "Unassigned").first()
    )
    return (
        session.query(Event)
        .filter(
            or_(
                Event.support_contact is None,
                Event.support_contact == unassigned_user,
            )
        )
        .all()
    )
