import sys
from src.daft_scraper import fetch_properties
from src.transport_stops import load_stops, nearest_stop
from src.html_generator import generate_html


def main(max_results: int = 200):
    print("Fetching properties from daft.ie...")
    properties = fetch_properties(max_results=max_results)
    print(f"Fetched {len(properties)} properties.")

    if not properties:
        print("No properties fetched. Exiting.")
        sys.exit(1)

    print("Loading transport stops...")
    stops_data = load_stops()

    print("Calculating nearest stops...")
    for prop in properties:
        prop.nearest_stop = nearest_stop(prop.lat, prop.lng, stops_data)

    properties.sort(key=lambda p: p.nearest_stop.get("distance_km", 999))

    print("Generating HTML...")
    generate_html(properties, output_path="docs/index.html")
    print("Done.")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    main(count)
