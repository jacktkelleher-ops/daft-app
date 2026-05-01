const PAGE_SIZE = 20;
const BASE_URL = 'https://www.daft.ie/property-for-sale/dublin';
const MAX_RESULTS = parseInt(process.argv[2] || '200');

async function fetchPage(from) {
  const url = `${BASE_URL}?salePrice_to=800000&pageSize=${PAGE_SIZE}&from=${from}&sort=publishDateDesc`;
  const res = await fetch(url);
  if (!res.ok) return null;
  const html = await res.text();
  const match = html.match(/<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/);
  if (!match) return [];
  const json = JSON.parse(match[1]);
  return json.props?.pageProps?.listings ?? [];
}

async function main() {
  const all = [];
  let from = 0;
  while (all.length < MAX_RESULTS) {
    const page = await fetchPage(from);
    if (page === null || page.length === 0) break;
    all.push(...page);
    if (page.length < PAGE_SIZE) break;
    from += PAGE_SIZE;
    await new Promise(r => setTimeout(r, 700));
  }
  process.stdout.write(JSON.stringify(all.slice(0, MAX_RESULTS)));
}

main().catch(e => { process.stderr.write(e.message + '\n'); process.exit(1); });
