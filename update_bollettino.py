import requests
import json
import sys

# --- CONFIGURAZIONE SORGENTI ---
# Il link che hai fornito (Sorgente ISTAT/OpenPolis EPSG:4326)
URL_GEOMETRIE = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_R_17_municipalities.geojson"
# Sorgente del bollettino
URL_BOLLETTINO = "https://raw.githubusercontent.com/Eatapples15/allerte_bollettino_basilicata/main/dati_bollettino.json"
FILE_OUTPUT = "bollettino_comunale_live.geojson"

# MAPPING ZONE (Nomi comuni normalizzati per questo specifico GeoJSON)
MAPPING_ZONE = {
    "Abriola": "BASI B", "Accettura": "BASI B", "Acerenza": "BASI B", "Albano di Lucania": "BASI B", "Aliano": "BASI C", "Anzi": "BASI B", "Armento": "BASI C", "Atella": "BASI A1", "Avigliano": "BASI B",
    "Balvano": "BASI A2", "Banzi": "BASI B", "Baragiano": "BASI A2", "Barile": "BASI A1", "Bella": "BASI A2", "Bernalda": "BASI E2", "Brienza": "BASI A2", "Brindisi Montagna": "BASI B", "Calciano": "BASI B", "Calvello": "BASI B", "Calvera": "BASI C", "Campomaggiore": "BASI B", "Cancellara": "BASI B", "Carbone": "BASI C", "Castelgrande": "BASI A2", "Castelluccio Inferiore": "BASI D", "Castelluccio Superiore": "BASI D", "Castelmezzano": "BASI B", "Castelsaraceno": "BASI D", "Castronuovo di Sant'Andrea": "BASI C", "Cersosimo": "BASI C", "Chiaromonte": "BASI C", "Cirigliano": "BASI C", "Colobraro": "BASI C", "Corleto Perticara": "BASI C", "Craco": "BASI E1", "Episcopia": "BASI C", "Fardella": "BASI C", "Ferrandina": "BASI B", "Filiano": "BASI A1", "Forenza": "BASI A1", "Francavilla in Sinni": "BASI C", "Gallicchio": "BASI C", "Garaguso": "BASI B", "Genzano di Lucania": "BASI B", "Ginestra": "BASI A1", "Gorgoglione": "BASI C", "Grassano": "BASI B", "Grottole": "BASI B", "Grumento Nova": "BASI C", "Guardia Perticara": "BASI C", "Irsina": "BASI B", "Lagonegro": "BASI D", "Latronico": "BASI D", "Laurenzana": "BASI B", "Lauria": "BASI D", "Lavello": "BASI A1", "Maratea": "BASI D", "Marsico Nuovo": "BASI C", "Marsicovetere": "BASI C", "Maschito": "BASI A1", "Matera": "BASI B", "Melfi": "BASI A1", "Miglionico": "BASI B", "Missanello": "BASI C", "Moliterno": "BASI C", "Montalbano Jonico": "BASI E1", "Montemilone": "BASI A1", "Montemurro": "BASI C", "Montescaglioso": "BASI E2", "Muro Lucano": "BASI A2", "Nemoli": "BASI D", "Noepoli": "BASI C", "Nova Siri": "BASI E1", "Oliveto Lucano": "BASI B", "Oppido Lucano": "BASI B", "Palazzo San Gervasio": "BASI A1", "Paterno": "BASI C", "Pescopagano": "BASI A1", "Picerno": "BASI A2", "Pietragalla": "BASI B", "Pietrapertosa": "BASI B", "Pignola": "BASI B", "Pisticci": "BASI E2", "Policoro": "BASI E1", "Pomarico": "BASI B", "Potenza": "BASI B", "Rapolla": "BASI A1", "Rapone": "BASI A1", "Rionero in Vulture": "BASI A1", "Ripacandida": "BASI A1", "Rivello": "BASI D", "Roccanova": "BASI C", "Rotonda": "BASI D", "Rotondella": "BASI E1", "Ruoti": "BASI A2", "Ruvo del Monte": "BASI A1", "Salandra": "BASI B", "San Chirico Nuovo": "BASI B", "San Chirico Raparo": "BASI C", "San Costantino Albanese": "BASI C", "San Fele": "BASI A1", "San Giorgio Lucano": "BASI C", "San Martino d'Agri": "BASI C", "San Mauro Forte": "BASI B", "San Paolo Albanese": "BASI C", "San Severino Lucano": "BASI C", "Sant'Angelo Le Fratte": "BASI A2", "Sant'Arcangelo": "BASI C", "Sarconi": "BASI C", "Sasso di Castalda": "BASI A2", "Satriano di Lucania": "BASI A2", "Savoia di Lucania": "BASI A2", "Scanzano Jonico": "BASI E1", "Senise": "BASI C", "Spinoso": "BASI C", "Stigliano": "BASI C", "Teana": "BASI C", "Terranova di Pollino": "BASI C", "Tito": "BASI A2", "Tolve": "BASI B", "Tramutola": "BASI C", "Trecchina": "BASI D", "Tricarico": "BASI B", "Trivigno": "BASI B", "Tursi": "BASI C", "Vaglio Basilicata": "BASI B", "Valsinni": "BASI C", "Venosa": "BASI A1", "Vietri di Potenza": "BASI A2", "Viggianello": "BASI D", "Viggiano": "BASI C"
}

def run_sync():
    print("🛰️ Recupero geometrie...")
    try:
        r_geo = requests.get(URL_GEOMETRIE, timeout=60)
        comuni_geo = r_geo.json()
    except Exception as e:
        print(f"❌ Errore geometrie: {e}")
        sys.exit(1)

    print("📡 Recupero bollettino...")
    try:
        r_alert = requests.get(URL_BOLLETTINO, timeout=30)
        alert_data = r_alert.json()
    except Exception as e:
        print(f"❌ Errore bollettino: {e}")
        sys.exit(1)

    print("🎨 Elaborazione stati allerta...")
    for feature in comuni_geo['features']:
        # In questo GeoJSON OpenPolis il nome è sotto 'name'
        nome_comune = feature['properties'].get('name', '').strip()
        
        zona = MAPPING_ZONE.get(nome_comune, "N.D.")
        # Estraiamo il colore di OGGI
        alert_info = alert_data['zone'].get(zona, {})
        colore = alert_info.get('oggi', 'green')
        rischio = alert_info.get('rischio_oggi', 'Assenza fenomeni significativi')

        # Inseriamo la proprietà 'allerta_stato' che il tuo SLD sta cercando
        feature['properties'] = {
            "allerta_stato": colore,
            "comune": nome_comune,
            "zona": zona,
            "rischio": rischio,
            "data_boll": alert_data.get("data_bollettino", "N.D.")
        }

    with open(FILE_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(comuni_geo, f, ensure_ascii=False)
    
    print(f"✅ Successo: {FILE_OUTPUT} generato correttamente.")

if __name__ == "__main__":
    run_sync()
