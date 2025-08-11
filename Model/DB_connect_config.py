import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os


def load_config(filename):
    DB_NAME = None
    load_dotenv(filename)
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    try:
        DB_NAME = os.getenv("DB_NAME")
    except:
        pass
    CONNEXION_CONFIG = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
    }
    if DB_NAME:
        CONNEXION_CONFIG["database"] = DB_NAME
    return CONNEXION_CONFIG


def db_connect(data):
    try:
        connexion = mysql.connector.connect(**data)
        cursor = connexion.cursor()
        return connexion, cursor
    except Error as e:
        print(f"Erreur lors de la connexion à la DB : {e}")
        stop_program()


def db_disconnect(cursor, connexion):
    print()
    print("Fermeture de la connexion...")
    if cursor:
        cursor.close()
    if connexion and connexion.is_connected():
        connexion.close()
    print("Toutes les connexions sont fermées.")


def stop_program():
    print("INSTALLATION TERMINEE !")
    exit()
