import requests
import datetime

# Official 2026 Open Data links from the CMA-mandated scheme
STATION_FEEDS = {
    "Asda": "https://storelocator.asda.com/fuel_prices_data.json",
    "Tesco": "https://www.tesco.com/fuel_prices/fuel_prices_data.json",
    "Sainsbury's": "https://api.sainsburys.co.uk/v1/exports/latest/fuel_prices_data.json",
    "Morrisons": "https://www.morrisons.com/fuel-prices/fuel.json",
    "BP": "https://www.bp.com/en_gb/united-kingdom/home/fuelprices/fuel_prices_data.json",
    "Shell": "https://www.shell.co.uk/fuel-prices-data.html" # Note: Shell often requires custom parsing
}

def get_preston_prices():
    html_rows = ""
    found_stations = []

    for brand, url in STATION_FEEDS.items():
        try:
            # Adding a browser-like User-Agent to prevent basic bot-blocking
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if response.status_code != 200: continue
            
            data = response.json()
            for station in data.get('stations', []):
                postcode = station.get('postcode', '')
                # Filter for Preston districts: PR1, PR2, PR3, PR4, PR5
                if postcode.startswith(('PR1', 'PR2', 'PR3', 'PR4', 'PR5')):
                    # Extract Diesel price
                    prices = station.get('prices', {})
                    # Some use 'Diesel', some use 'B7'
                    d_price = prices.get('Diesel') or prices.get('B7')
                    
                    if d_price:
                        found_stations.append({
                            'brand': brand,
                            'name': station.get('name', 'Forecourt'),
                            'postcode': postcode,
                            'price': float(d_price)
                        })
        except:
            continue

    # Sort by cheapest first
    found_stations.sort(key=lambda x: x['price'])

    for s in found_stations[:15]:
        html_rows += f"""
        <tr>
            <td><strong>{s['brand']}</strong> {s['name']}<br><small class='text-muted'>{s['postcode']}</small></td>
            <td class='text-end'><span class='price-badge'>{s['price']}p</span></td>
        </tr>"""
    
    return html_rows if html_rows else "<tr><td colspan='2'>No Preston data found. Retailers may be updating feeds.</td></tr>"

def generate_page(content):
    now = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preston Diesel Tracker</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background: #f8f9fa; padding: 20px; font-family: sans-serif; }}
            .card {{ border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: none; }}
            .price-badge {{ color: #198754; font-weight: bold; font-size: 1.2rem; }}
        </style>
    </head>
    <body>
        <div class="container" style="max-width: 500px;">
            <div class="text-center mb-4">
                <h2 class="fw-bold">⛽ Preston Diesel</h2>
                <p class="text-muted small">Live Open Data | {now}</p>
            </div>
            <div class="card p-3">
                <table class="table align-middle">
                    <thead><tr><th>Station</th><th class="text-end">Price</th></tr></thead>
                    <tbody>{content}</tbody>
                </table>
            </div>
        </div>
    </body>
    </html>"""
    with open("index.html", "w") as f:
        f.write(template)

if __name__ == "__main__":
    content = get_preston_prices()
    generate_page(content)
