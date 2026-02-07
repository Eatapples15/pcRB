import requests
import json
import os

# --- CONFIGURAZIONE EFFIS ---
# Usiamo il servizio WFS che restituisce dati vettoriali (punti)
URL_EFFIS_WFS = "https://effis.jrc.ec.europa.eu/static/effis_current/wfs"
FILE_OUTPUT = "effis_incendi_attivi.geojson"

def fetch_effis():
    print("📡 Collegamento a EFFIS (Copernicus) in corso...")
    
    # Parametri per estrarre solo gli incendi rilevati nelle ultime 24h
    params = {
        "service": "WFS",
        "version": "1.1.0",
        "request": "GetFeature",
        "typeName": "modis.fire.hotspots", # Punti caldi da satellite MODIS
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        # Filtriamo per l'area della Basilicata per non scaricare tutta Europa
        "bbox": "15.3,39.8,16.9,41.1,EPSG:4326"
    }

    try:
        r = requests.get(URL_EFFIS_WFS, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()

        # Salvataggio nella repo
        with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        
        print(f"✅ File {FILE_OUTPUT} generato con {len(data['features'])} incendi.")

    except Exception as e:
        print(f"❌ Errore durante il download da EFFIS: {e}")

if __name__ == "__main__":
    fetch_effis()
