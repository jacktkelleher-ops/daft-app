const fs = require('fs');
const path = require('path');

const BASE_URL = 'https://www.daft.ie/property-for-sale/dublin';
const DELAY_MS = 4000;
const CACHE_PATH = path.join(__dirname, 'data', 'listings.json');

const PRICE_BANDS = [
  [0,      200000],
  [200000, 300000],
  [300000, 400000],
  [400000, 500000],
  [500000, 600000],
  [600000, 700000],
  [700000, 800000],
];

async function fetchBand(from, to) {
  const url = `${BASE_URL}?salePrice_from=${from}&salePrice_to=${to}&pageSize=20&sort=publishDateDesc`;
  const res = await fetch(url);
  if (!res.ok) {
    process.stderr.write(`HTTP ${res.status} for band ${from}-${to}\n`);
    return [];
  }
  const html = await res.text();
  const match = html.match(/<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/);
  if (!match) return [];
  const json = JSON.parse(match[1]);
  return json.props?.pageProps?.listings ?? [];
}

async function main() {
  const seen = new Set();
  const all = [];

  for (const [from, to] of PRICE_BANDS) {
    process.stderr.write(`Fetching €${from/1000}k–€${to/1000}k...\n`);
    const page = await fetchBand(from, to);
    for (const item of page) {
      const id = item?.listing?.id;
      if (id && !seen.has(id)) {
        seen.add(id);
        all.push(item);
      }
    }
    await new Promise(r => setTimeout(r, DELAY_MS));
  }

  fs.writeFileSync(CACHE_PATH, JSON.stringify(all, null, 2), 'utf8');
  process.stderr.write(`Saved ${all.length} listings to ${CACHE_PATH}\n`);
}

main().catch(e => { process.stderr.write(e.message + '\n'); process.exit(1); });
