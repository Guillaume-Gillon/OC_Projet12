import Model.DB_create as DB_create

print()
print("VERIFICATION DE LA BASE DE DONNEES")
db_configurator = DB_create.DatabaseConfigurator()
if db_configurator.run_uninstall():
    print()
    print("L'application a été désinstallée avec succès !")
else:
    ("Abandon de la désinstallation.")
