import requests
import json
import os

# --- CONFIGURAZIONE ---
# Prendiamo i comuni dalla repo pcRB (il tuo file base)
URL_COMUNI_BASE = "https://raw.githubusercontent.com/Eatapples15/pcRB/main/basilicata_131_comuni.geojson"
# Il file dei dati è locale in questa repo
FILE_DATI = "dati_bollettino.json"
# Il file che WebSOR deve leggere
FILE_OUTPUT = "bollettino_comunale_live.geojson"

# Mapping Comuni -> Zone (Il tuo dizionario ufficiale)
MAPPING_ZONE = {
    "Abriola": "BASI B", "Accettura": "BASI B", "Acerenza": "BASI B", "Albano di Lucania": "BASI B", "Aliano": "BASI C", "Anzi": "BASI B", "Armento": "BASI C", "Atella": "BASI A1", "Avigliano": "BASI B",
    "Balvano": "BASI A2", "Banzi": "BASI B", "Baragiano": "BASI A2", "Barile": "BASI A1", "Bella": "BASI A2", "Bernalda": "BASI E2", "Brienza": "BASI A2", "Brindisi Montagna": "BASI B", "Calciano": "BASI B", "Calvello": "BASI B", "Calvera": "BASI C", "Campomaggiore": "BASI B", "Cancellara": "BASI B", "Carbone": "BASI C", "Castelgrande": "BASI A2", "Castelluccio Inferiore": "BASI D", "Castelluccio Superiore": "BASI D", "Castelmezzano": "BASI B", "Castelsaraceno": "BASI D", "Castronuovo di Sant' Andrea": "BASI C", "Cersosimo": "BASI C", "Chiaromonte": "BASI C", "Cirigliano": "BASI C", "Colobraro": "BASI C", "Corleto Perticara": "BASI C", "Craco": "BASI E1", "Episcopia": "BASI C", "Fardella": "BASI C", "Ferrandina": "BASI B", "Filiano": "BASI A1", "Forenza": "BASI A1", "Francavilla in Sinni": "BASI C", "Gallicchio": "BASI C", "Garaguso": "BASI B", "Genzano di Lucania": "BASI B", "Ginestra": "BASI A1", "Gorgoglione": "BASI C", "Grassano": "BASI B", "Grottole": "BASI B", "Grumento Nova": "BASI C", "Guardia Perticara": "BASI C", "Irsina": "BASI B", "Lagonegro": "BASI D", "Latronico": "BASI D", "Laurenzana": "BASI B", "Lauria": "BASI D", "Lavello": "BASI A1", "Maratea": "BASI D", "Marsico Nuovo": "BASI C", "Marsicovetere": "BASI C", "Maschito": "BASI A1", "Matera": "BASI B", "Melfi": "BASI A1", "Miglionico": "BASI B", "Missanello": "BASI C", "Moliterno": "BASI C", "Montalbano Jonico": "BASI E1", "Montemilone": "BASI A1", "Montemurro": "BASI C", "Montescaglioso": "BASI E2", "Muro Lucano": "BASI A2", "Nemoli": "BASI D", "Noepoli": "BASI C", "Nova Siri": "BASI E1", "Oliveto Lucano": "BASI B", "Oppido Lucano": "BASI B", "Palazzo San Gervasio": "BASI A1", "Paterno": "BASI C", "Pescopagano": "BASI A1", "Picerno": "BASI A2", "Pietragalla": "BASI B", "Pietrapertosa": "BASI B", "Pignola": "BASI B", "Pisticci": "BASI E2", "Policoro": "BASI E1", "Pomarico": "BASI B", "Potenza": "BASI B", "Rapolla": "BASI A1", "Rapone": "BASI A1", "Rionero in Vulture": "BASI A1", "Ripacandida": "BASI A1", "Rivello": "BASI D", "Roccanova": "BASI C", "Rotonda": "BASI D", "Rotondella": "BASI E1", "Ruoti": "BASI A2", "Ruvo del Monte": "BASI A1", "Salandra": "BASI B", "San Chirico Nuovo": "BASI B", "San Chirico Raparo": "BASI C", "San Costantino A.": "BASI C", "San Costantino Albanese": "BASI C", "S. Costantino Albanese": "BASI C", "San Fele": "BASI A1", "San Giorgio Lucano": "BASI C", "San Martino d'Agri": "BASI C", "San Mauro Forte": "BASI B", "San Paolo Albanese": "BASI C", "San Severino Lucano": "BASI C", "Sant' Angelo Le Fratte": "BASI A2", "Sant' Arcangelo": "BASI C", "Sarconi": "BASI C", "Sasso di Castalda": "BASI A2", "Satriano di Lucania": "BASI A2", "Savoia di Lucania": "BASI A2", "Scanzano Jonico": "BASI E1", "Senise": "BASI C", "Spinoso": "BASI C", "Stigliano": "BASI C", "Teana": "BASI C", "Terranova di Pollino": "BASI C", "Tito": "BASI A2", "Tolve": "BASI B", "Tramutola": "BASI C", "Trecchina": "BASI D", "Tricarico": "BASI B", "Trivigno": "BASI B", "Tursi": "BASI C", "Vaglio Basilicata": "BASI B", "Valsinni": "BASI C", "Venosa": "BASI A1", "Vietri di Potenza": "BASI A2", "Viggianello": "BASI D", "Viggiano": "BASI C"
}

def run():
    # 1. Scarichiamo i confini dei comuni dalla repo pcRB
    print("📡 Download confini comunali da pcRB...")
    r_geo = requests.get(URL_COMUNI_BASE)
    comuni_geo = r_geo.json()

    # 2. Leggiamo il bollettino locale
    print("📖 Lettura dati bollettino...")
    if not os.path.exists(FILE_DATI):
        print(f"❌ Errore: {FILE_DATI} non trovato!")
        return
    with open(FILE_DATI, 'r', encoding='utf-8') as f:
        dati_bollettino = json.load(f)

    # 3. Aggiorniamo le proprietà per WebSOR
    print("🔄 Aggiornamento stati allerta...")
    for feature in comuni_geo['features']:
        # Pulizia nome comune per il match
        nome_comune = feature['properties'].get('comune', '').strip()
        
        # Troviamo la zona BASI
        zona = MAPPING_ZONE.get(nome_comune, "N.D.")
        
        # Prendiamo il colore di OGGI dal bollettino
        # Se la zona non esiste, mettiamo green come fallback
        stato = dati_bollettino['zone'].get(zona, {}).get('oggi', 'green')
        rischio = dati_bollettino['zone'].get(zona, {}).get('rischio_oggi', 'Nessuno')

        # Assegniamo la proprietà esatta cercata dall'SLD
        feature['properties']['allerta_stato'] = stato
        feature['properties']['descrizione_rischio'] = rischio
        feature['properties']['zona_basi'] = zona

    # 4. Salviamo il file finale
    with open(FILE_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(comuni_geo, f, ensure_ascii=False)
    print(f"✅ Generato {FILE_OUTPUT} pronto per WebSOR.")

if __name__ == "__main__":
    run()
