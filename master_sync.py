import requests
import json
import os
import io
import zipfile
import shapefile
import xml.etree.ElementTree as ET
from pyproj import Transformer

# --- CONFIGURAZIONI ---
ENDPOINTS = {
    "standard": "https://rsdi.regione.basilicata.it/rbgeoserver2016/ows",
    "dpc_aggregati": "https://raw.githubusercontent.com/pcm-dpc/DPC-Aggregati-Strutturali-ITF-Sud/master/Sud/Basilicata/Basilicata_AggregatoStrutturale.zip"
}

# Mapping Comuni -> Zone Allerta
MAPPING_ZONE = {
    "Abriola": "BASI B", "Accettura": "BASI B", "Acerenza": "BASI B", "Albano di Lucania": "BASI B", "Aliano": "BASI C", "Anzi": "BASI B", "Armento": "BASI C", "Atella": "BASI A1", "Avigliano": "BASI B",
    "Balvano": "BASI A2", "Banzi": "BASI B", "Baragiano": "BASI A2", "Barile": "BASI A1", "Bella": "BASI A2", "Bernalda": "BASI E2", "Brienza": "BASI A2", "Brindisi Montagna": "BASI B", "Calciano": "BASI B", "Calvello": "BASI B", "Calvera": "BASI C", "Campomaggiore": "BASI B", "Cancellara": "BASI B", "Carbone": "BASI C", "Castelgrande": "BASI A2", "Castelluccio Inferiore": "BASI D", "Castelluccio Superiore": "BASI D", "Castelmezzano": "BASI B", "Castelsaraceno": "BASI D", "Castronuovo di Sant' Andrea": "BASI C", "Cersosimo": "BASI C", "Chiaromonte": "BASI C", "Cirigliano": "BASI C", "Colobraro": "BASI C", "Corleto Perticara": "BASI C", "Craco": "BASI E1", "Episcopia": "BASI C", "Fardella": "BASI C", "Ferrandina": "BASI B", "Filiano": "BASI A1", "Forenza": "BASI A1", "Francavilla in Sinni": "BASI C", "Gallicchio": "BASI C", "Garaguso": "BASI B", "Genzano di Lucania": "BASI B", "Ginestra": "BASI A1", "Gorgoglione": "BASI C", "Grassano": "BASI B", "Grottole": "BASI B", "Grumento Nova": "BASI C", "Guardia Perticara": "BASI C", "Irsina": "BASI B", "Lagonegro": "BASI D", "Latronico": "BASI D", "Laurenzana": "BASI B", "Lauria": "BASI D", "Lavello": "BASI A1", "Maratea": "BASI D", "Marsico Nuovo": "BASI C", "Marsicovetere": "BASI C", "Maschito": "BASI A1", "Matera": "BASI B", "Melfi": "BASI A1", "Miglionico": "BASI B", "Missanello": "BASI C", "Moliterno": "BASI C", "Montalbano Jonico": "BASI E1", "Montemilone": "BASI A1", "Montemurro": "BASI C", "Montescaglioso": "BASI E2", "Muro Lucano": "BASI A2", "Nemoli": "BASI D", "Noepoli": "BASI C", "Nova Siri": "BASI E1", "Oliveto Lucano": "BASI B", "Oppido Lucano": "BASI B", "Palazzo San Gervasio": "BASI A1", "Paterno": "BASI C", "Pescopagano": "BASI A1", "Picerno": "BASI A2", "Pietragalla": "BASI B", "Pietrapertosa": "BASI B", "Pignola": "BASI B", "Pisticci": "BASI E2", "Policoro": "BASI E1", "Pomarico": "BASI B", "Potenza": "BASI B", "Rapolla": "BASI A1", "Rapone": "BASI A1", "Rionero in Vulture": "BASI A1", "Ripacandida": "BASI A1", "Rivello": "BASI D", "Roccanova": "BASI C", "Rotonda": "BASI D", "Rotondella": "BASI E1", "Ruoti": "BASI A2", "Ruvo del Monte": "BASI A1", "Salandra": "BASI B", "San Chirico Nuovo": "BASI B", "San Chirico Raparo": "BASI C", "San Costantino A.": "BASI C", "San Costantino Albanese": "BASI C", "S. Costantino Albanese": "BASI C", "San Fele": "BASI A1", "San Giorgio Lucano": "BASI C", "San Martino d'Agri": "BASI C", "San Mauro Forte": "BASI B", "San Paolo Albanese": "BASI C", "San Severino Lucano": "BASI C", "Sant' Angelo Le Fratte": "BASI A2", "Sant' Arcangelo": "BASI C", "Sarconi": "BASI C", "Sasso di Castalda": "BASI A2", "Satriano di Lucania": "BASI A2", "Savoia di Lucania": "BASI A2", "Scanzano Jonico": "BASI E1", "Senise": "BASI C", "Spinoso": "BASI C", "Stigliano": "BASI C", "Teana": "BASI C", "Terranova di Pollino": "BASI C", "Tito": "BASI A2", "Tolve": "BASI B", "Tramutola": "BASI C", "Trecchina": "BASI D", "Tricarico": "BASI B", "Trivigno": "BASI B", "Tursi": "BASI C", "Vaglio Basilicata": "BASI B", "Valsinni": "BASI C", "Venosa": "BASI A1", "Vietri di Potenza": "BASI A2", "Viggianello": "BASI D", "Viggiano": "BASI C"
}

TRANSFORMER = Transformer.from_crs("epsg:32633", "epsg:4326", always_xy=True)

def reproject_any(coords):
    if isinstance(coords[0], (int, float)):
        return list(TRANSFORMER.transform(coords[0], coords[1]))
    return [reproject_any(c) for c in coords]

def get_base_comuni():
    print("🏙️ Recupero confini comunali da RSDI...")
    # Proviamo diversi nomi layer possibili sulla RSDI Basilicata
    possible_layers = ["rsdi:basi_comuni", "rsdi:comuni_pol", "rsdi:limiti_comunali"]
    
    for layer in possible_layers:
        params = {
            "service": "WFS", "version": "1.1.0", "request": "GetFeature", 
            "typeName": layer, "outputFormat": "application/json"
        }
        try:
            r = requests.get(ENDPOINTS["standard"], params=params, timeout=60)
            r.raise_for_status()
            
            # Verifichiamo se la risposta è effettivamente un JSON
            if "application/json" in r.headers.get("Content-Type", ""):
                data = r.json()
                for f in data['features']:
                    f['geometry']['coordinates'] = reproject_any(f['geometry']['coordinates'])
                with open("basilicata_131_comuni.geojson", "w") as f:
                    json.dump(data, f)
                print(f"✅ Confini recuperati con successo usando layer: {layer}")
                return data
            else:
                print(f"⚠️ Il server ha risposto con formato non JSON per {layer}. Messaggio: {r.text[:100]}")
        except Exception as e:
            print(f"❌ Fallimento su layer {layer}: {e}")
            
    print("🛑 Impossibile trovare il layer dei comuni. Verifica il catalogo RSDI.")
    return None

def process_alerts(comuni_base):
    if not comuni_base: return
    print("⛈️ Elaborazione bollettino allerta...")
    if not os.path.exists("dati_bollettino.json"):
        print("⚠️ File dati_bollettino.json mancante.")
        return
    with open("dati_bollettino.json", "r") as f: alert_data = json.load(f)
    
    for p in ['oggi', 'domani']:
        features = []
        for feat in comuni_base['features']:
            f = json.loads(json.dumps(feat))
            comune = f['properties'].get('comune', '').title()
            zona = MAPPING_ZONE.get(comune, "N.D.")
            info = alert_data['zone'].get(zona, {"oggi": "green", "domani": "green", "rischio_oggi": "Nessuno", "rischio_domani": "Nessuno"})
            f['properties'].update({
                "allerta_colore": info[p], "rischio": info[f'rischio_{p}'], "zona": zona, "data_boll": alert_data['data_bollettino']
            })
            features.append(f)
        with open(f"allerta_{p}.geojson", "w") as out:
            json.dump({"type": "FeatureCollection", "features": features}, out)

def get_aggregati():
    print("🏗️ Scaricamento Aggregati DPC...")
    try:
        r = requests.get(ENDPOINTS["dpc_aggregati"])
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
        with open("dpc_aggregati_basilicata.geojson", "w") as f: json.dump(agg_geo, f)
        print("✅ Aggregati sismici salvati.")
    except Exception as e: print(f"❌ Errore Aggregati: {e}")

if __name__ == "__main__":
    comuni = get_base_comuni()
    if comuni:
        process_alerts(comuni)
    get_aggregati()
    print("🏁 Sync terminato.")
