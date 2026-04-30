import json
import math
from pathlib import Path


def load_stops() -> dict:
    stops_path = Path(__file__).parent.parent / "data" / "stops.json"
    with open(stops_path) as f:
        return json.load(f)


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def nearest_stop(lat: float, lng: float, stops_data: dict) -> dict:
    best = {"name": None, "type": None, "distance_km": float("inf")}

    for line_name, stops in stops_data["luas"].items():
        label = "Luas " + line_name.replace("_", " ").title()
        for stop in stops:
            d = haversine_km(lat, lng, stop["lat"], stop["lng"])
            if d < best["distance_km"]:
                best = {"name": stop["name"], "type": label, "distance_km": round(d, 2)}

    for stop in stops_data["dart"]:
        d = haversine_km(lat, lng, stop["lat"], stop["lng"])
        if d < best["distance_km"]:
            best = {"name": stop["name"], "type": "DART", "distance_km": round(d, 2)}

    return best
