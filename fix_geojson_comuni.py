import json
import os
from pyproj import Transformer

def fix_comuni():
    input_file = "basilicata_131_comuni.geojson"
    output_file = "basilicata_131_comuni_fixed.geojson"
    
    if not os.path.exists(input_file):
        print("❌ File originale non trovato!")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Configuriamo il trasformatore da EPSG:25833 (il tuo file) a EPSG:4326 (WebSOR)
    transformer = Transformer.from_crs("epsg:25833", "epsg:4326", always_xy=True)

    def transform_coords(coords):
        if isinstance(coords[0], (int, float)):
            return list(transformer.transform(coords[0], coords[1]))
        return [transform_coords(c) for c in coords]

    print("🔄 Trasformazione coordinate e pulizia nomi in corso...")
    
    new_features = []
    for feat in data['features']:
        # 1. Trasformazione Coordinate
        feat['geometry']['coordinates'] = transform_coords(feat['geometry']['coordinates'])
        
        # 2. Normalizzazione Proprietà
        # Prendiamo 'nome_com' (ABRIOLA) e creiamo 'comune' (Abriola)
        original_name = feat['properties'].get('nome_com', '')
        clean_name = original_name.strip().title()
        
        feat['properties'] = {
            "comune": clean_name,
            "cod_istat": feat['properties'].get('comune_ist', ''),
            "provincia": feat['properties'].get('nome_prov', '').title()
        }
        new_features.append(feat)

    data['features'] = new_features
    # Rimuoviamo il vecchio CRS per non confondere WebSOR
    if 'crs' in data: del data['crs']

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    
    print(f"✅ File riparato creato: {output_file}")

if __name__ == "__main__":
    fix_comuni()
