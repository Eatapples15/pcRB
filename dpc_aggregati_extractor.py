import requests
import zipfile
import io
import json
import os
import shapefile # Richiede pip install pyshp
from pyproj import Transformer

# --- CONFIGURAZIONE ---
URL_DPC_BASILICATA = "https://raw.githubusercontent.com/pcm-dpc/DPC-Aggregati-Strutturali-ITF-Sud/master/Sud/Basilicata/Basilicata_AggregatoStrutturale.zip"
FILE_OUTPUT = "dpc_aggregati_basilicata.geojson"

# Trasformatore: UTM 33N (DPC) -> WGS84 (WebSOR)
TRANSFORMER = Transformer.from_crs("epsg:32633", "epsg:4326", always_xy=True)

def reproject_coords(coords):
    if isinstance(coords[0], (int, float)):
        return list(TRANSFORMER.transform(coords[0], coords[1]))
    return [reproject_coords(c) for c in coords]

def extract_dpc_data():
    print("📡 Download Aggregati Strutturali dal repository DPC...")
    r = requests.get(URL_DPC_BASILICATA, timeout=120)
    
    # Estrazione in memoria
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extractall("temp_dpc")
    
    # Individuazione del file .shp
    shp_file = [f for f in os.listdir("temp_dpc") if f.endswith(".shp")][0]
    shp_path = os.path.join("temp_dpc", shp_file)

    print("🔄 Conversione in GeoJSON e riproiezione coordinate...")
    reader = shapefile.Reader(shp_path)
    fields = [f[0] for f in reader.fields[1:]]
    geojson_data = {"type": "FeatureCollection", "features": []}

    for sr in reader.shapeRecords():
        # Riproiezione geometria
        new_coords = reproject_coords(sr.shape.__geo_interface__['coordinates'])
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": sr.shape.__geo_interface__['type'],
                "coordinates": new_coords
            },
            "properties": dict(zip(fields, sr.record))
        }
        geojson_data["features"].append(feature)

    # Salvataggio finale
    with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, ensure_ascii=False)
    
    print(f"✅ Successo! Layer aggregati salvato in: {FILE_OUTPUT}")

if __name__ == "__main__":
    extract_dpc_data()
