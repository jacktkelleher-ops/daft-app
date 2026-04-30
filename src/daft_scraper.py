import time
import random
import requests
from dataclasses import dataclass, field


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IE,en;q=0.9",
    "Referer": "https://www.daft.ie/",
}

DAFT_API = "https://gateway.daft.ie/old/v1/listings"

DEFAULT_PARAMS = {
    "section": "residential-for-rent",
    "geoFilter[storedShapeIds][]": "3",  # Dublin
    "paging[from]": "0",
    "paging[pageSize]": "50",
}


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


def _parse_property(item: dict) -> Property | None:
    try:
        listing = item.get("listing", item)
        coords = listing.get("point", {})
        lat = coords.get("coordinates", [None, None])[1]
        lng = coords.get("coordinates", [None, None])[0]
        if not lat or not lng:
            return None

        price_val = listing.get("price", "N/A")
        if isinstance(price_val, (int, float)):
            price = f"€{price_val:,}/mo"
        else:
            price = str(price_val)

        media = listing.get("media", {})
        images = media.get("images", [])
        image_url = images[0].get("size720x480", "") if images else ""

        num_beds = listing.get("numBedrooms", "")
        num_baths = listing.get("numBathrooms", "")

        return Property(
            id=listing.get("id", 0),
            title=listing.get("title", ""),
            price=price,
            address=listing.get("seoFriendlyPath", "").replace("/", " ").strip() or listing.get("title", ""),
            url=f"https://www.daft.ie{listing.get('seoFriendlyPath', '')}",
            lat=float(lat),
            lng=float(lng),
            bedrooms=str(num_beds) if num_beds else "",
            bathrooms=str(num_baths) if num_baths else "",
            property_type=listing.get("propertyType", ""),
            image_url=image_url,
        )
    except Exception:
        return None


def fetch_properties(max_results: int = 100, section: str = "residential-for-rent") -> list[Property]:
    properties = []
    page_size = 50
    fetched = 0

    session = requests.Session()
    session.headers.update(HEADERS)

    while fetched < max_results:
        params = {
            **DEFAULT_PARAMS,
            "section": section,
            "paging[from]": str(fetched),
            "paging[pageSize]": str(min(page_size, max_results - fetched)),
        }

        try:
            resp = session.get(DAFT_API, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Error fetching page at offset {fetched}: {e}")
            break

        listings = data.get("listings", [])
        if not listings:
            break

        for item in listings:
            prop = _parse_property(item)
            if prop:
                properties.append(prop)

        fetched += len(listings)
        if len(listings) < page_size:
            break

        time.sleep(random.uniform(0.5, 1.2))

    return properties
