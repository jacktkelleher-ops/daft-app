from dataclasses import dataclass, field

from daft_scraper.search import DaftSearch, SearchType
from daft_scraper.search.options import PriceOption, SortOption, Sort
from daft_scraper.search.options_location import LocationsOption, Location


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


def _to_property(listing) -> Property | None:
    try:
        coords = listing.point.coordinates if listing.point else None
        if not coords or len(coords) < 2:
            return None
        lng, lat = coords[0], coords[1]

        price = f"€{int(listing.price):,}/mo" if listing.price else "N/A"

        images = listing.media.images if listing.media else []
        image_url = images[0].get("size720x480", "") if images else ""

        return Property(
            id=listing.id,
            title=listing.title or "",
            price=price,
            address=listing.title or "",
            url=listing.url or "",
            lat=float(lat),
            lng=float(lng),
            bedrooms=str(listing.numBedrooms) if listing.numBedrooms else "",
            bathrooms=str(listing.numBathrooms) if listing.numBathrooms else "",
            property_type=listing.propertyType or "",
            image_url=image_url,
        )
    except Exception:
        return None


def fetch_properties(max_results: int = 100, section: str = "residential-for-rent") -> list[Property]:
    options = [
        LocationsOption([Location.DUBLIN_COUNTY]),
        PriceOption(0, 99999),
        SortOption(Sort.BEST_MATCH),
    ]

    api = DaftSearch(SearchType.RENT)
    listing_gen = api.search(options)

    properties = []
    for listing in listing_gen:
        if len(properties) >= max_results:
            break
        prop = _to_property(listing)
        if prop:
            properties.append(prop)

    return properties
