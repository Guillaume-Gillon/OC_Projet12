from Model import DB_connect_config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import urllib.parse

import os


def connect_app_to_db():

    connexion_config_file = "Config/user_config.env"
    if not os.path.exists(connexion_config_file):
        print("Le fichier de configuration 'user_config.env' n'a pas été trouvé.")
        print(
            "Vérifiez l'existence de la base de données. Si elle n'existe pas, exécutez 'install.py'."
        )
        return None, None
    connexion_data = DB_connect_config.load_config(connexion_config_file)
    if (
        not connexion_data["host"]
        or not connexion_data["port"]
        or not connexion_data["user"]
        or not connexion_data["password"]
    ):
        print("Connexion impossible.")
        print("Vérifier le fichier 'Config/user_config.env'.")
        return None, None
    db_user = connexion_data["user"]
    db_encoded_user_password = urllib.parse.quote_plus(connexion_data["password"])
    db_host = connexion_data["host"]
    db_name = connexion_data["database"]

    engine = create_engine(
        f"mysql+mysqlconnector://{db_user}:{db_encoded_user_password}@{db_host}/{db_name}"
    )

    Session = sessionmaker(bind=engine)
    session = Session()
    return session, engine


def disconnect_app_from_db(session, engine=None):
    success = True
    try:
        if session:
            session.close()
    except Exception as e:
        print(f"Erreur lors de la fermeture de la session : {e}")
        success = False

    try:
        if engine:
            engine.dispose()
            print("L'application a été fermée.")
    except Exception as e:
        print(f"Erreur lors de la disposition de l'engine : {e}")
        success = False
    return success
