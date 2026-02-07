import requests
import zipfile
import io
import json
import os
import shapefile
import sys
from pyproj import Transformer

# --- CONFIGURAZIONE ---
# URL specifico per il download di file grandi (LFS) su GitHub
URL_DPC_BASILICATA = "https://media.githubusercontent.com/media/pcm-dpc/DPC-Aggregati-Strutturali-ITF-Sud/master/Sud/Basilicata/Basilicata_AggregatoStrutturale.zip"
FILE_OUTPUT = "dpc_aggregati_basilicata.geojson"
TEMP_DIR = "temp_dpc"

# Trasformatore: UTM 33N -> WGS84
TRANSFORMER = Transformer.from_crs("epsg:32633", "epsg:4326", always_xy=True)

def reproject_coords(coords):
    if isinstance(coords[0], (int, float)):
        return list(TRANSFORMER.transform(coords[0], coords[1]))
    return [reproject_coords(c) for c in coords]

def extract_dpc_data():
    print(f"📡 Download Aggregati Strutturali dal server media DPC...")
    
    try:
        # Download con timeout esteso per file grandi
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(URL_DPC_BASILICATA, headers=headers, timeout=300)
        r.raise_for_status()
        
        # Verifica se è un file reale o un puntatore LFS (i puntatori sono < 500 byte)
        if len(r.content) < 1000:
            print("❌ Errore: Il server ha restituito un puntatore LFS invece del file ZIP.")
            print("Verifica l'URL o i limiti di banda LFS della repo DPC.")
            sys.exit(1)

        print(f"📦 Download completato ({len(r.content) / 1024 / 1024:.2f} MB). Estrazione...")
        
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            if not os.path.exists(TEMP_DIR):
                os.makedirs(TEMP_DIR)
            z.extractall(TEMP_DIR)
        
        # Individuazione del file .shp
        shp_file = [f for f in os.listdir(TEMP_DIR) if f.endswith(".shp")][0]
        shp_path = os.path.join(TEMP_DIR, shp_file)

        print(f"🔄 Conversione {shp_file} in GeoJSON e riproiezione coordinate...")
        reader = shapefile.Reader(shp_path)
        fields = [f[0] for f in reader.fields[1:]]
        geojson_data = {"type": "FeatureCollection", "features": []}

        for sr in reader.shapeRecords():
            geom = sr.shape.__geo_interface__
            # Riproiezione geometria (poligoni strutturali)
            new_coords = reproject_coords(geom['coordinates'])
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": geom['type'],
                    "coordinates": new_coords
                },
                "properties": dict(zip(fields, sr.record))
            }
            geojson_data["features"].append(feature)

        # Salvataggio finale
        with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(geojson_data, f, ensure_ascii=False)
        
        print(f"✅ Layer aggregati sismici pronto: {FILE_OUTPUT}")

    except Exception as e:
        print(f"❌ Errore durante l'estrazione DPC: {e}")
        sys.exit(1)

if __name__ == "__main__":
    extract_dpc_data()
