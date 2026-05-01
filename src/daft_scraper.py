import json
import re
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
    price_val: int
    address: str
    url: str
    lat: float
    lng: float
    bedrooms: str = ""
    beds_num: int = 0
    bathrooms: str = ""
    property_type: str = ""
    image_url: str = ""
    ber: str = ""
    nearest_stop: dict = field(default_factory=dict)


def _parse_listing(item: dict) -> Property | None:
    try:
        listing = item.get("listing", item)
        coords = listing.get("point", {}).get("coordinates", [None, None])
        lng, lat = coords[0], coords[1]
        if not lat or not lng:
            return None

        raw_price = listing.get("price", 0)
        if isinstance(raw_price, (int, float)):
            price_val = int(raw_price)
        else:
            digits = re.sub(r"[^\d]", "", str(raw_price))
            price_val = int(digits) if digits else 0
        price = f"€{price_val:,}" if price_val else str(raw_price)

        beds_raw = listing.get("numBedrooms", "")
        beds_match = re.search(r"\d+", str(beds_raw)) if beds_raw else None
        beds_num = int(beds_match.group()) if beds_match else 0

        ber_data = listing.get("ber", {})
        if isinstance(ber_data, dict):
            ber = ber_data.get("rating", "")
        else:
            ber = str(ber_data) if ber_data else ""
        if ber and ber[0].upper() not in "ABCDEFG":
            ber = ""

        images = listing.get("media", {}).get("images", [])
        image_url = images[0].get("size720x480", "") if images else ""

        return Property(
            id=listing.get("id", 0),
            title=listing.get("title", ""),
            price=price,
            price_val=price_val,
            address=listing.get("seoFriendlyPath", "").replace("/", " ").strip() or listing.get("title", ""),
            url=f"https://www.daft.ie{listing.get('seoFriendlyPath', '')}",
            lat=float(lat),
            lng=float(lng),
            bedrooms=str(beds_num) if beds_num else "",
            beds_num=beds_num,
            bathrooms=str(listing.get("numBathrooms", "")) if listing.get("numBathrooms") else "",
            property_type=listing.get("propertyType", ""),
            image_url=image_url,
            ber=ber,
        )
    except Exception:
        return None


def fetch_properties(max_results: int = 200) -> list[Property]:
    result = subprocess.run(
        ["node", str(FETCHER), str(max_results)],
        capture_output=True, text=True, encoding="utf-8", timeout=180
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
