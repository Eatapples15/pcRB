import requests
import json
import os
import sys

# --- CONFIGURAZIONE ---
URL_WFS = "https://effis.jrc.ec.europa.eu/static/effis_current/wfs"
FILE_OUTPUT = "effis_incendi_attivi.geojson"

def fetch_effis():
    print("📡 Collegamento ai satelliti Copernicus EFFIS...")
    
    params = {
        "service": "WFS",
        "version": "1.1.0",
        "request": "GetFeature",
        "typeName": "modis.fire.hotspots", 
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "bbox": "15.3,39.8,16.9,41.1,EPSG:4326" 
    }

    try:
        r = requests.get(URL_WFS, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        
        # Se non ci sono incendi, creiamo una struttura GeoJSON vuota standard
        if not data or 'features' not in data:
            data = {"type": "FeatureCollection", "features": []}
            print("ℹ️ Nessun incendio rilevato dai satelliti.")
        else:
            print(f"🔥 Rilevati {len(data['features'])} potenziali incendi.")

        # SCRITTURA FORZATA: Garantisce che il file esista sempre per Git
        with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        
        print(f"✅ File {FILE_OUTPUT} salvato correttamente.")

    except Exception as e:
        print(f"❌ Errore durante l'estrazione: {e}")
        # Creiamo un file vuoto di emergenza per evitare l'errore di Git Add
        empty_data = {"type": "FeatureCollection", "features": [], "note": "Errore download"}
        with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(empty_data, f)
        sys.exit(0) # Usciamo con successo per non bloccare il workflow

if __name__ == "__main__":
    fetch_effis()
