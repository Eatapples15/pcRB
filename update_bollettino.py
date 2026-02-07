import requests
import json
import os

# --- CONFIGURAZIONE ---
FILE_COMUNI_FIXED = "basilicata_131_comuni_fixed.geojson"
URL_BOLLETTINO = "https://raw.githubusercontent.com/Eatapples15/allerte_bollettino_basilicata/main/dati_bollettino.json"
FILE_OUTPUT_WEBSOR = "bollettino_comunale_live.geojson"

# (Inserisci qui il dizionario MAPPING_ZONE completo che abbiamo usato prima)

def update_websor():
    if not os.path.exists(FILE_COMUNI_FIXED):
        print("❌ Esegui prima fix_geojson_comuni.py!")
        return

    with open(FILE_COMUNI_FIXED, 'r', encoding='utf-8') as f:
        comuni_geo = json.load(f)
    
    r = requests.get(URL_BOLLETTINO)
    alert_data = r.json()

    for feat in comuni_geo['features']:
        nome = feat['properties']['comune'] # Ora è già "Abriola" grazie al fix
        zona = MAPPING_ZONE.get(nome, "NON CENSITA")
        
        info = alert_data['zone'].get(zona, {"oggi": "green", "rischio_oggi": "Nessuno"})
        
        # Proprietà cercata dal tuo SLD
        feat['properties']['allerta_stato'] = info['oggi']
        feat['properties']['descrizione'] = info['rischio_oggi']
        feat['properties']['zona_basi'] = zona

    with open(FILE_OUTPUT_WEBSOR, 'w', encoding='utf-8') as f:
        json.dump(comuni_geo, f, ensure_ascii=False)
    print("✅ Mappa colorata generata!")

if __name__ == "__main__":
    update_websor()
