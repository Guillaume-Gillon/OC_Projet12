from argon2 import PasswordHasher, Type as Argon2Type
from argon2.exceptions import VerifyMismatchError


def ph_instance():
    PH = PasswordHasher(
        time_cost=2,
        memory_cost=102400,
        parallelism=2,
        hash_len=16,
        salt_len=16,
        type=Argon2Type.ID,
    )
    return PH


def hash_password(password):
    PH = ph_instance()
    hashed_password = PH.hash(password)
    return hashed_password


def verify_password(hashed_password, password):
    PH = ph_instance()
    try:
        if not isinstance(hashed_password, str) or not hashed_password:
            return False
        PH.verify(hashed_password, password)
        return True
    except VerifyMismatchError:
        print("ERREUR : Mot de passe incorrect.")
        return False
