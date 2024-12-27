import requests
import json
from datetime import datetime
from .sucheingabe import Sucheingabe  # Aladdine: Sucheingabe wird importiert, um Haltestellen zu verwalten

def verbindungssuche(dockwidget):  # Aladdine: dockwidget wird als Parameter hinzugefügt, um die IDs abzurufen
    # URL der API
    url = "https://webapi.vvo-online.de/tr/trips?format=json"

    # Header für die Anfrage
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'X-Requested-With': 'de.dvb.dvbmobil'
    }

    # Aladdine: Initialisierung des Sucheingabe-Objekts zur Abfrage der Haltestellen-IDs
    sucheingabe = Sucheingabe(dockwidget)
    hsStart = sucheingabe.getStartHaltestelleID()  # Aladdine: Start-Haltestelle-ID wird abgerufen
    hsZiel = sucheingabe.getZielHaltestelleID()    # Aladdine: Ziel-Haltestelle-ID wird abgerufen

    # Aktuelles Datum / Zeit aus den Eingabefeldern laden 
    DatumAusTextfeld = dockwidget.verbindungssuche_input_datum.text()  # Aladdine: Datum aus dem Textfeld wird gelesen
    UhrzeitAusTextfeld = dockwidget.verbindungssuche_input_uhrzeit.text()  # Aladdine: Uhrzeit aus dem Textfeld wird gelesen
    current_time = DatumAusTextfeld + UhrzeitAusTextfeld  # Aladdine: Datum und Uhrzeit werden kombiniert

    # Daten für den POST-Request
    data = {
        "destination": hsStart,  # Aladdine: hsStart wird verwendet, um die Start-Haltestelle zu setzen
        "isarrivaltime": False,
        "mobilitySettings": {
            "mobilityRestriction": "None"
        },
        "origin": hsZiel,  # Aladdine: hsZiel wird für die Ziel-Haltestelle verwendet
        "shorttermchanges": True,
        "standardSettings": {
            "footpathToStop": 5,
            "includeAlternativeStops": True,
            "maxChanges": "Unlimited",
            "mot": [
                "Tram",
                "CityBus",
                "IntercityBus",
                "SuburbanRailway",
                "Train",
                "Cableway",
                "Ferry",
                "HailedSharedTaxi"
            ],
            "walkingSpeed": "Normal"
        },
        "time": current_time  # Aladdine: Aktuelle Zeit wird in die Anfrage integriert
    }

    # POST-Anfrage senden
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # String für die Ausgabe der Verbindungen
    output = ""

    # Überprüfen, ob die Anfrage erfolgreich war
    if response.status_code == 200:
        result = response.json()

        if 'Routes' in result:
            Routes1 = result['Routes']
            max_connections = 5
            available_routes = len(Routes1)

            if available_routes == 0:
                output += "Keine Verbindungen gefunden.\n"  # Aladdine: Nachricht, wenn keine Verbindungen verfügbar sind
            else:
                for i, route in enumerate(Routes1[:max_connections]):
                    duration = route.get('Duration', "Keine Dauer verfügbar")  # Aladdine: Dauer der Verbindung wird abgerufen
                    mot_chain = route.get('MotChain', [])  # Aladdine: Liste der Verkehrsmittel
                    num_changes = len(mot_chain) - 1  # Aladdine: Anzahl der Umstiege wird berechnet
                    linien_richtungen = []

                    for mot in mot_chain:
                        direction = mot.get('Direction', "Keine Richtung verfügbar")  # Aladdine: Richtung des Verkehrsmittels
                        linie = mot.get('Name', "Keine Linie verfügbar")  # Aladdine: Name der Linie wird abgerufen
                        linien_richtungen.append(f"{linie} ({direction})")  # Aladdine: Linie und Richtung werden kombiniert

                    partial_routes = route.get('PartialRoutes', [])  # Aladdine: Teilstrecken der Route

                    if partial_routes:
                        first_partial_route = partial_routes[0]  # Aladdine: Erste Teilstrecke wird abgerufen
                        first_regular_stop = first_partial_route.get('RegularStops', [])[0]  # Aladdine: Erster regulärer Stopp
                        departure_time_str = first_regular_stop.get('DepartureTime', "")

                        last_partial_route = partial_routes[-1]  # Aladdine: Letzte Teilstrecke wird abgerufen
                        last_regular_stop = last_partial_route.get('RegularStops', [])[-1]  # Aladdine: Letzter regulärer Stopp
                        arrival_time_str = last_regular_stop.get('ArrivalTime', "")

                        if departure_time_str:
                            timestamp = int(departure_time_str[6:19]) / 1000  # Aladdine: Zeitstempel wird in lesbares Format umgewandelt
                            departure_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                        else:
                            departure_time = "Keine Abfahrtszeit verfügbar"

                        if arrival_time_str:
                            timestamp = int(arrival_time_str[6:19]) / 1000
                            arrival_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                        else:
                            arrival_time = "Keine Ankunftszeit verfügbar"

                        output += "-" * 50 + "\n"
                        output += f"Verbindung #{i + 1}\n"
                        output += f"Dauer: {duration} Minuten\n"
                        output += f"Linien: {', '.join(linien_richtungen)}\n"
                        output += f"Abfahrtszeit: {departure_time}\n"
                        output += f"Ankunftszeit: {arrival_time}\n"
                        output += f"Umstiege: {num_changes}\n"
                        output += "-" * 50 + "\n"
                
                if available_routes < max_connections:
                    output += f"Nur {available_routes} Verbindungen gefunden.\n"
        else:
            output += "Keine Routen gefunden.\n"
    else:
        output += f"Fehler bei der Anfrage: {response.status_code}\n"

    return output
