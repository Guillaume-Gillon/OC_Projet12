import Model.DB_create as DB_create
import Model.DB_init_tables as DB_init_tables
import Model.DB_connect_config as DB_connect_config


print()
print("VERIFICATION DE LA BASE DE DONNEES")
db_configurator = DB_create.DatabaseConfigurator()
if db_configurator.run_setup():
    data = db_configurator.get_data()

    db_name = data["db_name"]
    cursor = data["cursor"]
    connexion = data["db_conn"]
    admin_username = data["admin_username"]
    admin_password = data["admin_password"]
    host = data["host"]

    print()
    print("INITIALISATION DE LA BASE DE DONNEES")
    print("Creation des tables ...")
    DB_init_tables.create_tables(admin_username, admin_password, host, db_name)

    query = f"USE {db_name}"
    cursor.execute(query)
    print("Création de l'utilisateur 'Unassigned Element' ...")
    DB_init_tables.create_unassigned_user(cursor, connexion)
    print("Création des rôles ...")
    roles = DB_init_tables.create_roles(cursor, connexion)
    print("Création des permissions ...")
    permissions = DB_init_tables.create_permissions(cursor, connexion)
    print("Attribution des permissions pour chaque rôle ...")
    DB_init_tables.assign_permissions_to_roles(cursor, connexion)
else:
    print("Fermeture du programme...")
    exit()


DB_connect_config.db_disconnect(cursor, connexion)
DB_connect_config.stop_program()
