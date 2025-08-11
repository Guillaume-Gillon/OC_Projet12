import re
import getpass


def check_password_strength(password) -> bool:
    # Exigences de base : au moins 12 caractères, majuscule, minuscule, chiffre, caractère spécial
    if len(password) < 12:
        print("ERREUR : Le mot de passe doit contenir au moins 12 caractères.")
        return False
    if not re.search(r"[a-z]", password):
        print("ERREUR : Le mot de passe doit contenir au moins une minuscule.")
        return False
    if not re.search(r"[A-Z]", password):
        print("ERREUR : Le mot de passe doit contenir au moins une majuscule.")
        return False
    if not re.search(r"\d", password):
        print("ERREUR : Le mot de passe doit contenir au moins un chiffre.")
        return False
    if not re.search(r"[!#$%^&*()_+=\-{}[\]|\\:;\"'<>,.?/`~]", password):
        print("ERREUR : Le mot de passe doit contenir au moins un caractère spécial.")
        return False
    return True


def password_validation():
    same_passwords = False
    valid_password = False
    while not same_passwords:
        while not valid_password:
            password = getpass.getpass(
                "Mot de passe (12 car. majuscule, minuscule, chiffre, car. spé.) : "
            )
            if check_password_strength(password):
                valid_password = True
        password_again = getpass.getpass("Confirmez le mot de passe : ")
        if password_again == password:
            same_passwords = True
    return password
