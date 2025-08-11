from rich.console import Console
from rich.table import Table


# --- AFFICHER LES CLIENTS ---
def clients_table(clients):
    table = Table(title="Clients")

    table.add_column("Société", justify="center", style="cyan")
    table.add_column("Nom du contact", justify="center", style="magenta")
    table.add_column("Téléphone", justify="center", style="green")
    table.add_column("E-mail", justify="center", style="green")
    table.add_column("Contact Epic Events", justify="center", style="cyan")

    for client in clients:
        table.add_row(
            client.company_name,
            client.name,
            client.phone_number,
            client.email,
            f"{client.commercial_contact.first_name} {client.commercial_contact.last_name}",
        )

    console = Console()
    console.print(table)
    input("Tapez entrée pour quitter")


# --- AFFICHER LES CONTRATS ---
def contracts_table(contracts):
    table = Table(title="Contrats")

    table.add_column("Client", justify="center", style="cyan")
    table.add_column("Montant", justify="center", style="magenta")
    table.add_column("Reste à payer", justify="center", style="green")
    table.add_column("Contact Epic Event", justify="center", style="green")
    table.add_column("Statut", justify="center", style="green")

    for contract in contracts:
        if contract.signed:
            signed = "Signé"
        else:
            signed = "Non signé"
        table.add_row(
            contract.client.company_name,
            str(contract.amount),
            str(contract.balance_due),
            f"{contract.commercial_contact.first_name} {contract.commercial_contact.last_name}",
            signed,
        )

    console = Console()
    console.print(table)
    input("Tapez entrée pour quitter")


# --- AFFICHER LES EVENEMENTS ---
def events_table(events):
    table = Table(title="Evènements")

    table.add_column("Libellé", justify="right", style="cyan")
    table.add_column("Données", justify="left", style="green")

    for event in events:
        from Controller.contract_manager import decode_contract_id
        from Controller.global_manager import date_format_for_display

        table.add_row("Nom", str(event.name))
        table.add_row("ID évènement", str(event.id))

        contract_id = decode_contract_id(event.contract)
        table.add_row("ID contrat", str(contract_id))
        table.add_row(
            "Client",
            f"{event.contract.client.name} ({event.contract.client.company_name})",
        )
        table.add_row(
            "Coordonnées",
            f"{event.contract.client.phone_number} - {event.contract.client.email}",
        )
        table.add_row("Date de début", str(date_format_for_display(event.start_at)))
        table.add_row("Date de fin", str(date_format_for_display(event.end_at)))
        if event.support_contact:
            table.add_row(
                "Contact Epic Event",
                f"{event.support_contact.first_name} {event.support_contact.last_name}",
            )
        else:
            table.add_row("Contact Epic Event", "Aucun contact enregistré.")
        table.add_row("Lieu", event.location)
        table.add_row("Nombre de personnes", str(event.attendees))
        table.add_row("Notes", event.notes)

    console = Console()
    console.print(table)
    input("Tapez entrée pour quitter")
