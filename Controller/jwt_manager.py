import jwt
import keyring
import time
import datetime
import secrets

SERVICE_NAME = "EpicEventsCRM"
APPLICATION_NAME = "EE_jwt_secret"


def get_or_generate_jwt_signing_secret():
    secret = keyring.get_password(SERVICE_NAME, APPLICATION_NAME)
    if not secret:
        secret = secrets.token_urlsafe(64)
        keyring.set_password(SERVICE_NAME, APPLICATION_NAME, secret)
    return secret


JWT_SIGNING_SECRET = get_or_generate_jwt_signing_secret()
JWT_TOKEN_KEY_NAME = "user_jwt_token"


def store_jwt_token(token):
    """Stocke le JWT de l'utilisateur dans le password manager de l'OS."""
    try:
        keyring.set_password(SERVICE_NAME, JWT_TOKEN_KEY_NAME, token)
        return True
    except Exception as e:
        print(f"Erreur lors du stockage du JWT : {e}")
        return False


def delete_jwt_token_from_password_manager():
    """Supprime le JWT de l'utilisateur et la clé secrète stockés dans le password manager de l'OS."""
    try:
        keyring.delete_password(SERVICE_NAME, JWT_TOKEN_KEY_NAME)
        keyring.delete_password(SERVICE_NAME, APPLICATION_NAME)
        return True
    except keyring.errors.NoKeyringError:
        print("Aucun trousseau de clés disponible ou configuré sur ce système.")
        return False
    except Exception as e:
        print(f"Erreur : {e}")
        return False


def get_jwt_token():
    """Récupère le JWT de l'utilisateur dans le password manager de l'OS."""
    try:
        token = keyring.get_password(SERVICE_NAME, JWT_TOKEN_KEY_NAME)
        if token:
            return token
    except Exception as e:
        print(f"Erreur lors de la récupération du JWT : {e}")
        return None


def generate_jwt(user_id, permissions):
    payload = {
        "sub": str(user_id),
        "iat": int(time.time()),  # Issued At (heure d'émission)
        "exp": get_valid_duration(),
        "permissions": permissions,
    }
    encoded_jwt = jwt.encode(payload, JWT_SIGNING_SECRET, algorithm="HS256")
    return encoded_jwt


def get_valid_duration():
    now = datetime.datetime.now(datetime.timezone.utc)
    valid_duration = now + datetime.timedelta(minutes=2)
    return valid_duration


def decode_jwt(token):
    try:
        decoded_payload = jwt.decode(token, JWT_SIGNING_SECRET, algorithms=["HS256"])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None


def load_jwt():
    valid_token = False
    decoded_payload = None
    token = None
    token = get_jwt_token()
    if token:
        decoded_payload = decode_jwt(token)
        if decoded_payload:
            valid_token = True
    return valid_token, decoded_payload, token


def create_jwt(current_user_id, permissions):
    new_jwt = generate_jwt(current_user_id, permissions)
    if new_jwt:
        if store_jwt_token(new_jwt):
            return new_jwt
    return None
