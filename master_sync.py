import json
import os
import requests
import io
import zipfile
import shapefile
from pyproj import Transformer

# --- CONFIGURAZIONI ---
INPUT_COMUNI = "basilicata_131_comuni.geojson"
URL_AGGREGATI = "https://raw.githubusercontent.com/pcm-dpc/DPC-Aggregati-Strutturali-ITF-Sud/master/Sud/Basilicata/Basilicata_AggregatoStrutturale.zip"

# Il tuo dizionario di mappatura (Assicurati che i nomi coincidano col GeoJSON)
MAPPING_ZONE = {
    "Abriola": "BASI B", "Accettura": "BASI B", "Tito": "BASI A2", "Potenza": "BASI B",
    # ... inserisci qui tutto il dizionario completo che abbiamo visto prima ...
}

TRANSFORMER = Transformer.from_crs("epsg:32633", "epsg:4326", always_xy=True)

def reproject_any(coords):
    if isinstance(coords[0], (int, float)):
        return list(TRANSFORMER.transform(coords[0], coords[1]))
    return [reproject_any(c) for c in coords]

def run_sync():
    print("🚀 Avvio Master Sync su repo pcRB...")
    
    # 1. Caricamento dei comuni dal TUO file locale
    if not os.path.exists(INPUT_COMUNI):
        print(f"🛑 ERRORE: Il file {INPUT_COMUNI} non è presente nella cartella!")
        return
    
    with open(INPUT_COMUNI, 'r', encoding='utf-8') as f:
        comuni_geo = json.load(f)
    print(f"✅ Base comunale caricata: {len(comuni_geo['features'])} comuni.")

    # 2. Generazione Allerta Meteo (Oggi e Domani)
    if os.path.exists("dati_bollettino.json"):
        with open("dati_bollettino.json", "r", encoding='utf-8') as f:
            alert_data = json.load(f)
        
        for p in ['oggi', 'domani']:
            features = []
            for feat in comuni_geo['features']:
                f = json.loads(json.dumps(feat)) # Copia profonda
                # Match del nome (cerca 'comune' o 'nome' nelle proprietà)
                nome = f['properties'].get('comune') or f['properties'].get('nome') or ""
                nome = nome.strip()
                
                zona = MAPPING_ZONE.get(nome, "N.D.")
                info = alert_data['zone'].get(zona, {"oggi": "green", "domani": "green", "rischio_oggi": "Assenza fenomeni", "rischio_domani": "Assenza fenomeni"})
                
                f['properties'].update({
                    "allerta_colore": info[p],
                    "rischio": info[f'rischio_{p}'],
                    "zona": zona
                })
                features.append(f)
            
            with open(f"allerta_{p}.geojson", "w", encoding='utf-8') as out:
                json.dump({"type": "FeatureCollection", "features": features}, out)
        print("✅ Layer allerta_oggi.geojson e allerta_domani.geojson generati.")

    # 3. Aggregati Strutturali DPC
    print("🏗️ Aggiornamento Aggregati DPC...")
    try:
        r = requests.get(URL_AGGREGATI, timeout=60)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall("temp_dpc")
        shp_file = [f for f in os.listdir("temp_dpc") if f.endswith(".shp")][0]
        sf = shapefile.Reader(f"temp_dpc/{shp_file}")
        agg_geo = {"type": "FeatureCollection", "features": []}
        for sr in sf.shapeRecords():
            coords = [reproject_any(pt) for pt in sr.shape.points]
            agg_geo["features"].append({
                "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [coords]},
                "properties": sr.record.as_dict()
            })
        with open("dpc_aggregati_basilicata.geojson", "w") as f:
            json.dump(agg_geo, f)
        print("✅ Aggregati DPC pronti.")
    except Exception as e:
        print(f"⚠️ Errore aggregati (saltato): {e}")

if __name__ == "__main__":
    run_sync()
