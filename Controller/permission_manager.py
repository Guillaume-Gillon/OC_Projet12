from View.display_messages import display_message
from Controller import jwt_manager
import functools


def permission_required(permission, payload_required=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(auth_token, *args, **kwargs):
            if not auth_token:
                display_message(
                    "Accès refusé : Le jeton d'authentification n'a pas été fourni."
                )
                return None
            payload = jwt_manager.decode_jwt(auth_token)
            if not payload or permission not in payload.get("permissions", []):
                display_message(f"Accès refusé.")
                return None

            # Si tout est bon, on appelle la fonction
            if payload_required:
                return func(payload, *args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def get_roles_and_su_permission():
    """
    Récupère la liste de tous les rôles et indique si chacun est un superutilisateur.

    Returns:
        List[tuple[str, bool]]: Une liste de tuples, où chaque tuple contient (role_name, is_superuser).
    """
    roles = [
        ("collaborateur", 0),
        ("commercial", 0),
        ("support", 0),
        ("gestion", 0),
    ]
    return roles


def get_permissions_and_description():
    """
    Récupère la liste des permissions et sa description.

    Returns:
        List[tuple[str, str]]: Une liste de tuples, où chaque tuple contient (permission_name, description).
    """
    permissions = [
        ("create:user", "Créer un utilisateur"),
        ("read:user", "Lire les informations sur les utilisateurs"),
        ("update:user", "Modifier un utilisateur"),
        ("delete:user", "Supprimer un utilisateur"),
        ("create:client", "Créer un client"),
        ("read:client", "Lire les informations sur les clients"),
        ("update:client", "Modifier un client"),
        ("create:contract", "Créer un contrat"),
        ("read:contract", "Lire les informations sur les contrats"),
        ("update:contract", "Modifier un contrat"),
        ("create:event", "Créer un évènement"),
        ("read:event", "Lire les informations sur les évènements"),
        ("update:event", "Modifier un évènement"),
    ]
    return permissions
