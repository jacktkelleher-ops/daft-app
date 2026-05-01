import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

CHROME_PROFILE = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
CACHE = Path(__file__).parent / "data" / "listings.json"
SEARCH_URL = "https://www.daft.ie/property-for-sale/dublin?salePrice_to=800000"


def fetch():
    all_listings = []
    seen_ids = set()

    with sync_playwright() as p:
        print("Launching Chrome with your profile (Chrome must be closed)...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE),
            channel="chrome",
            headless=False,
            args=["--profile-directory=Default"],
        )
        page = context.new_page()

        def on_response(response):
            if "gateway.daft.ie" in response.url and response.status == 200:
                try:
                    data = response.json()
                    new = 0
                    for item in data.get("listings", []):
                        lid = item.get("listing", {}).get("id")
                        if lid and lid not in seen_ids:
                            seen_ids.add(lid)
                            all_listings.append(item)
                            new += 1
                    if new:
                        print(f"  +{new} listings (total: {len(all_listings)})")
                except Exception:
                    pass

        page.on("response", on_response)

        print(f"Navigating to search page...")
        page.goto(SEARCH_URL)
        page.wait_for_load_state("load")
        time.sleep(4)

        try:
            accept = page.locator("button:has-text('Accept')")
            if accept.is_visible(timeout=3000):
                accept.click()
                time.sleep(1)
        except Exception:
            pass

        print("Clicking 'Load more' until all listings are loaded...")
        while True:
            prev = len(all_listings)
            try:
                btn = page.locator("button:has-text('Load more'), button:has-text('Show more results')")
                if btn.count() > 0 and btn.first.is_visible(timeout=5000):
                    btn.first.scroll_into_view_if_needed()
                    btn.first.click()
                    time.sleep(3)
                    if len(all_listings) == prev:
                        print("No new listings after click, stopping.")
                        break
                else:
                    print("No more results to load.")
                    break
            except Exception:
                break

        context.close()

    CACHE.write_text(json.dumps(all_listings, indent=2), encoding="utf-8")
    print(f"\nSaved {len(all_listings)} listings to {CACHE}")


if __name__ == "__main__":
    fetch()
