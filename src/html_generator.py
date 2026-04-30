from datetime import datetime, timezone


def generate_html(properties: list, output_path: str = "docs/index.html") -> None:
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cards = ""

    for p in properties:
        stop = p.nearest_stop
        stop_name = stop.get("name", "Unknown")
        stop_type = stop.get("type", "")
        dist = stop.get("distance_km", "?")

        stop_class = "dart" if "DART" in stop_type else "luas-green" if "Green" in stop_type else "luas-red"
        img_html = f'<img src="{p.image_url}" alt="" loading="lazy">' if p.image_url else '<div class="no-img">No image</div>'
        beds = f'<span class="tag">{p.bedrooms} bed</span>' if p.bedrooms else ""
        baths = f'<span class="tag">{p.bathrooms} bath</span>' if p.bathrooms else ""
        prop_type = f'<span class="tag">{p.property_type}</span>' if p.property_type else ""

        cards += f"""
    <div class="card" data-dist="{dist}">
      <a href="{p.url}" target="_blank" rel="noopener">
        <div class="card-img">{img_html}</div>
        <div class="card-body">
          <div class="price">{p.price}</div>
          <div class="address">{p.title}</div>
          <div class="tags">{beds}{baths}{prop_type}</div>
          <div class="stop {stop_class}">
            <span class="stop-icon">🚉</span>
            <strong>{dist} km</strong> to {stop_name} <em>({stop_type})</em>
          </div>
        </div>
      </a>
    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daft.ie — Properties for Sale &amp; Distance to Luas/DART</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: system-ui, sans-serif; background: #f4f5f7; color: #1a1a2e; }}

    header {{
      background: #1a1a2e;
      color: #fff;
      padding: 1.5rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}
    header h1 {{ font-size: 1.4rem; }}
    header p {{ font-size: 0.85rem; opacity: 0.7; }}

    .controls {{
      padding: 1rem 2rem;
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      align-items: center;
      background: #fff;
      border-bottom: 1px solid #e0e0e0;
    }}
    .controls label {{ font-size: 0.9rem; font-weight: 500; }}
    select, input[type=range] {{ cursor: pointer; }}
    #dist-label {{ font-weight: 600; min-width: 4rem; }}

    .legend {{
      display: flex;
      gap: 1rem;
      padding: 0.75rem 2rem;
      font-size: 0.8rem;
      flex-wrap: wrap;
    }}
    .legend span {{ display: flex; align-items: center; gap: 0.3rem; }}
    .dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
    .dot.dart {{ background: #00b050; }}
    .dot.luas-green {{ background: #3d9a27; }}
    .dot.luas-red {{ background: #e0001b; }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1.25rem;
      padding: 1.5rem 2rem;
      max-width: 1400px;
      margin: 0 auto;
    }}

    .card {{
      background: #fff;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,.08);
      transition: transform 0.15s, box-shadow 0.15s;
    }}
    .card:hover {{ transform: translateY(-3px); box-shadow: 0 6px 16px rgba(0,0,0,.12); }}
    .card a {{ text-decoration: none; color: inherit; display: flex; flex-direction: column; height: 100%; }}

    .card-img {{ height: 180px; overflow: hidden; background: #e8e8e8; }}
    .card-img img {{ width: 100%; height: 100%; object-fit: cover; }}
    .no-img {{ display: flex; align-items: center; justify-content: center; height: 100%; color: #aaa; font-size: 0.85rem; }}

    .card-body {{ padding: 0.9rem; flex: 1; display: flex; flex-direction: column; gap: 0.4rem; }}
    .price {{ font-size: 1.15rem; font-weight: 700; color: #1a1a2e; }}
    .address {{ font-size: 0.82rem; color: #555; line-height: 1.3; }}
    .tags {{ display: flex; gap: 0.3rem; flex-wrap: wrap; margin-top: 0.2rem; }}
    .tag {{ background: #f0f0f0; padding: 0.15rem 0.5rem; border-radius: 20px; font-size: 0.75rem; }}

    .stop {{ margin-top: auto; padding-top: 0.6rem; font-size: 0.82rem; border-top: 1px solid #f0f0f0; }}
    .stop.dart {{ color: #007a3d; }}
    .stop.luas-green {{ color: #2d7a1f; }}
    .stop.luas-red {{ color: #b0000e; }}

    #no-results {{ display: none; text-align: center; padding: 3rem; color: #888; grid-column: 1/-1; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Daft.ie &mdash; For Sale &bull; Luas &amp; DART Distance</h1>
      <p>{len(properties)} properties &bull; Updated {updated}</p>
    </div>
  </header>

  <div class="controls">
    <label for="sort">Sort by:</label>
    <select id="sort">
      <option value="dist">Distance to stop</option>
      <option value="price-asc">Price (low to high)</option>
      <option value="price-desc">Price (high to low)</option>
    </select>

    <label for="max-dist">Max distance: <span id="dist-label">any</span></label>
    <input type="range" id="max-dist" min="0.1" max="5" step="0.1" value="5">

    <label for="filter-type">Transport:</label>
    <select id="filter-type">
      <option value="all">All</option>
      <option value="DART">DART only</option>
      <option value="Luas">Luas only</option>
    </select>
  </div>

  <div class="legend">
    <span><span class="dot dart"></span> DART</span>
    <span><span class="dot luas-green"></span> Luas Green Line</span>
    <span><span class="dot luas-red"></span> Luas Red Line</span>
  </div>

  <div class="grid" id="grid">
    {cards}
    <div id="no-results">No properties match your filters.</div>
  </div>

  <script>
    const grid = document.getElementById('grid');
    const cards = Array.from(grid.querySelectorAll('.card'));
    const noResults = document.getElementById('no-results');

    function parsePrice(card) {{
      const text = card.querySelector('.price').textContent.replace(/[€,\\/mo\\s]/g, '');
      return parseFloat(text) || 0;
    }}

    function applyFilters() {{
      const sortVal = document.getElementById('sort').value;
      const maxDist = parseFloat(document.getElementById('max-dist').value);
      const typeFilter = document.getElementById('filter-type').value;

      document.getElementById('dist-label').textContent = maxDist >= 5 ? 'any' : maxDist.toFixed(1) + ' km';

      let visible = cards.filter(c => {{
        const dist = parseFloat(c.dataset.dist);
        if (dist > maxDist) return false;
        if (typeFilter !== 'all') {{
          const stopText = c.querySelector('.stop').textContent;
          if (!stopText.includes(typeFilter)) return false;
        }}
        return true;
      }});

      if (sortVal === 'dist') visible.sort((a, b) => parseFloat(a.dataset.dist) - parseFloat(b.dataset.dist));
      else if (sortVal === 'price-asc') visible.sort((a, b) => parsePrice(a) - parsePrice(b));
      else if (sortVal === 'price-desc') visible.sort((a, b) => parsePrice(b) - parsePrice(a));

      const visibleSet = new Set(visible);
      cards.forEach(c => {{ c.style.display = visibleSet.has(c) ? '' : 'none'; }});
      visible.forEach(c => grid.appendChild(c));
      noResults.style.display = visible.length === 0 ? 'block' : 'none';
    }}

    document.getElementById('sort').addEventListener('change', applyFilters);
    document.getElementById('max-dist').addEventListener('input', applyFilters);
    document.getElementById('filter-type').addEventListener('change', applyFilters);

    applyFilters();
  </script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated {output_path} with {len(properties)} properties.")
