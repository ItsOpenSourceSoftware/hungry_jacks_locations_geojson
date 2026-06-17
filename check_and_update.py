import requests
import json
from datetime import datetime

API_URL = "https://www.hungryjacks.com.au/api/storelist"
OUTPUT_FILE = "stores.geojson"
RAW_CACHE = "raw_cache.json"

def fetch():
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    return r.json()

def to_float(x):
    try:
        return float(x)
    except:
        return None

def build_geojson(stores):
    features = []

    for s in stores:
        loc = s.get("location", {})

        lat = to_float(loc.get("lat"))
        lon = to_float(loc.get("long"))

        if lat is None or lon is None:
            continue

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "store_id": s.get("store_id"),
                "name": s.get("name"),
                "suburb": loc.get("suburb"),
                "state": loc.get("state"),
                "address": loc.get("address"),
                "postcode": loc.get("postcode"),
                "phone": loc.get("phone"),
                "is24x7": s.get("facilities", {}).get("is24x7"),
                "drive_thru": s.get("facilities", {}).get("drivethru")
            }
        })

    return {
        "type": "FeatureCollection",
        "metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "source": API_URL,
            "count": len(features)
        },
        "features": features
    }

def load_previous():
    try:
        with open(RAW_CACHE, "r") as f:
            return json.load(f)
    except:
        return None

def save(raw, geojson):
    with open(RAW_CACHE, "w") as f:
        json.dump(raw, f)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(geojson, f, indent=2)

def main():
    print("Fetching store data...")

    raw = fetch()
    new_data = json.dumps(raw, sort_keys=True)

    old = load_previous()
    old_data = json.dumps(old, sort_keys=True) if old else None

    if new_data != old_data:
        print("Change detected → updating GeoJSON")
        geo = build_geojson(raw)
        save(raw, geo)
    else:
        print("No changes")

if __name__ == "__main__":
    main()
