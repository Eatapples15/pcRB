import requests
import json
from datetime import datetime

# --- NUOVA CONFIGURAZIONE UFFICIALE ---
# URL aggiornato dalle istruzioni Copernicus
URL_BASE = "https://maps.effis.emergency.copernicus.eu/effis"
FILE_OUTPUT = "effis_incendi_attivi.geojson"

def fetch_effis_updated():
    # Otteniamo la data odierna nel formato richiesto (YYYY-MM-DD)
    oggi = datetime.now().strftime("%Y-%m-%d")
    print(f"📡 Interrogazione EFFIS per la data: {oggi}")

    params = {
        "SERVICE": "WFS",
        "VERSION": "1.1.0",
        "REQUEST": "GetFeature",
        "TYPENAME": "modis.fire.hotspots",
        "OUTPUTFORMAT": "application/json",
        "SRSNAME": "EPSG:4326",
        "TIME": oggi, # Fondamentale come indicato nelle istruzioni
        "BBOX": "15.3,39.8,16.9,41.1,EPSG:4326"
    }

    try:
        r = requests.get(URL_BASE, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()

        with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        
        print(f"✅ Layer aggiornato con successo: {len(data.get('features', []))} incendi trovati.")

    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    fetch_effis_updated()
