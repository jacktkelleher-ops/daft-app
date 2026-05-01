import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


FETCHER = Path(__file__).parent.parent / "fetch_daft.js"


@dataclass
class Property:
    id: int
    title: str
    price: str
    address: str
    url: str
    lat: float
    lng: float
    bedrooms: str = ""
    bathrooms: str = ""
    property_type: str = ""
    image_url: str = ""
    nearest_stop: dict = field(default_factory=dict)


def _parse_listing(item: dict) -> Property | None:
    try:
        listing = item.get("listing", item)
        coords = listing.get("point", {}).get("coordinates", [None, None])
        lng, lat = coords[0], coords[1]
        if not lat or not lng:
            return None

        price_val = listing.get("price", "N/A")
        price = f"€{int(price_val):,}" if isinstance(price_val, (int, float)) else str(price_val)

        images = listing.get("media", {}).get("images", [])
        image_url = images[0].get("size720x480", "") if images else ""

        return Property(
            id=listing.get("id", 0),
            title=listing.get("title", ""),
            price=price,
            address=listing.get("seoFriendlyPath", "").replace("/", " ").strip() or listing.get("title", ""),
            url=f"https://www.daft.ie{listing.get('seoFriendlyPath', '')}",
            lat=float(lat),
            lng=float(lng),
            bedrooms=str(listing.get("numBedrooms", "")) if listing.get("numBedrooms") else "",
            bathrooms=str(listing.get("numBathrooms", "")) if listing.get("numBathrooms") else "",
            property_type=listing.get("propertyType", ""),
            image_url=image_url,
        )
    except Exception:
        return None


def fetch_properties(max_results: int = 200) -> list[Property]:
    result = subprocess.run(
        ["node", str(FETCHER), str(max_results)],
        capture_output=True, text=True, timeout=180
    )
    if result.returncode != 0:
        print(f"fetch_daft.js error: {result.stderr.strip()}", file=sys.stderr)
        return []

    raw = json.loads(result.stdout)
    seen = set()
    properties = []
    for item in raw:
        prop = _parse_listing(item)
        if prop and prop.id not in seen:
            seen.add(prop.id)
            properties.append(prop)
    return properties
