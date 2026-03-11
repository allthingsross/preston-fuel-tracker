import requests
import datetime
import json

# Verified 2026 Statutory Open Data URLs
STATION_FEEDS = {
    "Asda": "https://storelocator.asda.com/fuel_prices_data.json",
    "Tesco": "https://www.tesco.com/fuel_prices/fuel_prices_data.json",
    "Sainsbury's": "https://api.sainsburys.co.uk/v1/exports/latest/fuel_prices_data.json",
    "Morrisons": "https://www.morrisons.com/fuel-prices/fuel.json",
    "BP": "https://www.bp.com/en_gb/united-kingdom/home/fuelprices/fuel_prices_data.json",
    "Shell": "https://www.shell.co.uk/fuel-prices-data.json",
    "MFG (Gulf/Texaco)": "https://fuel.motorfuelgroup.com/fuel_prices_data.json",
    "Applegreen": "https://applegreenstores.com/fuel-prices/data.json",
    "Rontec (Esso)": "https://www.rontec-servicestations.co.uk/fuel-prices/data/fuel_prices_data.json"
}

def get_preston_prices():
    found_stations = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for brand, url in STATION_FEEDS.items():
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200: continue
            
            data = response.json()
            stations = data.get('stations', [])
            
            for s in stations:
                pc = str(s.get('postcode', '')).upper().replace(" ", "")
                # Wider Preston filter (PR1-PR5)
                if pc.startswith(('PR1', 'PR2', 'PR3', 'PR4', 'PR5')):
                    prices = s.get('prices', {})
                    
                    # 2026 Logic: Check for Diesel OR the new standard B7 label
                    # Shell and BP often use 'B7' exclusively now.
                    price_val = prices.get('Diesel') or prices.get('B7') or prices.get('diesel')
                    
                    if price_val:
                        found_stations.append({
                            'brand': brand,
                            'name': s.get('name', 'Forecourt'),
                            'postcode': s.get('postcode', ''),
                            'price': float(price_val)
                        })
        except:
            continue

    found_stations.sort(key=lambda x: x['price'])
    
    # Build HTML rows
    rows = ""
    for s in found_stations:
        rows += f"<tr><td><span class='station-name'>{s['brand']} {s['name']}</span><br><small class='text-muted'>{s['postcode']}</small></td><td class='text-end'><span class='price-badge'>{s['price']}p</span></td></tr>"
    return rows if rows else "<tr><td colspan='2'>No Preston stations found.</td></tr>"

def generate_webpage(content):
    now = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preston Fuel</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background: #f0f2f5; padding-top: 20px; font-family: sans-serif; }}
            .card {{ border-radius: 15px; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .price-badge {{ color: #198754; font-weight: bold; font-size: 1.2rem; }}
            .station-name {{ font-weight: 600; color: #212529; }}
            .sticky-header {{ position: sticky; top: 0; background: #f0f2f5; padding-bottom: 10px; z-index: 10; }}
        </style>
    </head>
    <body>
        <div class="container" style="max-width: 500px;">
            <div class="sticky-header text-center">
                <h2 class="fw-bold m-0">⛽ Preston Diesel</h2>
                <p class="text-muted small">Updated {now}</p>
                <input type="text" id="search" class="form-control shadow-sm" placeholder="Search (e.g. Morrisons, PR2)...">
            </div>
            <div class="card p-3 mt-2">
                <table class="table table-hover align-middle mb-0" id="fuelTable">
                    <thead><tr><th>Station</th><th class="text-end">Price</th></tr></thead>
                    <tbody>{content}</tbody>
                </table>
            </div>
        </div>
        <script>
            document.getElementById('search').addEventListener('keyup', function() {{
                const val = this.value.toLowerCase();
                document.querySelectorAll('#fuelTable tbody tr').forEach(row => {{
                    row.style.display = row.textContent.toLowerCase().includes(val) ? '' : 'none';
                }});
            }});
        </script>
    </body>
    </html>
    """
    with open("index.html", "w") as f:
        f.write(html)

if __name__ == "__main__":
    generate_webpage(get_preston_prices())
