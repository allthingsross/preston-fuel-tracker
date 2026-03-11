import requests
import datetime
import json

# Official 2026 Open Data links
STATION_FEEDS = {
    "Asda": "https://storelocator.asda.com/fuel_prices_data.json",
    "Tesco": "https://www.tesco.com/fuel_prices/fuel_prices_data.json",
    "Sainsbury's": "https://api.sainsburys.co.uk/v1/exports/latest/fuel_prices_data.json",
    "Morrisons": "https://images.morrisons.com/petrol-prices/petrol.json",
    "BP": "https://www.bp.com/en_gb/united-kingdom/home/fuelprices/fuel_prices_data.json",
    "Shell": "https://www.shell.co.uk/fuel-prices-data.json",
    "MFG (Gulf/Texaco)": "https://fuel.motorfuelgroup.com/fuel_prices_data.json",
    "Applegreen": "https://applegreenstores.com/fuel-prices/data.json"
}

def get_preston_prices():
    html_rows = ""
    found_stations = []

    for brand, url in STATION_FEEDS.items():
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code != 200:
                continue
            
            data = response.json()
            stations_list = data.get('stations', [])
            
            for station in stations_list:
                pc = str(station.get('postcode', '')).upper().replace(" ", "")
                if pc.startswith(('PR1', 'PR2', 'PR3', 'PR4', 'PR5')):
                    prices = station.get('prices', {})
                    # Catching various Diesel labels used in 2026
                    d_price = prices.get('Diesel') or prices.get('B7') or prices.get('diesel')
                    
                    if d_price:
                        found_stations.append({
                            'brand': brand,
                            'name': station.get('name', 'Forecourt'),
                            'postcode': station.get('postcode', ''),
                            'price': float(d_price)
                        })
        except:
            continue

    found_stations.sort(key=lambda x: x['price'])

    if not found_stations:
        return "<tr><td colspan='2' class='text-center'>No live data found for Preston.</td></tr>"

    for s in found_stations:
        html_rows += f"<tr><td><span class='station-name'>{s['brand']} {s['name']}</span><br><small class='text-muted'>{s['postcode']}</small></td><td class='text-end'><span class='price-badge'>{s['price']}p</span></td></tr>"
    
    return html_rows
def generate_webpage(content):
    now = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    
    # Note: Double curly braces {{ }} are used to escape CSS/JS for Python's f-string
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preston Fuel Tracker</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f0f2f5; padding-top: 20px; font-family: sans-serif; }}
            .card {{ border-radius: 15px; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .price-badge {{ color: #198754; font-weight: bold; font-size: 1.2rem; }}
            .station-name {{ font-weight: 600; color: #212529; }}
            .sticky-search {{ position: sticky; top: 0; background: #f0f2f5; z-index: 100; padding-bottom: 15px; }}
        </style>
    </head>
    <body>
        <div class="container" style="max-width: 500px;">
            <div class="sticky-search">
                <div class="text-center mb-3">
                    <h2 class="fw-bold m-0">⛽ Preston Diesel</h2>
                    <p class="text-muted small m-0">Updated {now}</p>
                </div>
                <input type="text" id="fuelSearch" class="form-control form-control-lg shadow-sm" 
                       placeholder="Search station or area (e.g. Asda, PR2)...">
            </div>

            <div class="card p-3 bg-white">
                <table class="table table-hover align-middle mb-0" id="fuelTable">
                    <thead><tr><th>Station</th><th class="text-end">Price</th></tr></thead>
                    <tbody>
                        {content}
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            // Real-time Search Logic
            document.getElementById('fuelSearch').addEventListener('keyup', function() {{
                const filter = this.value.toLowerCase();
                const rows = document.querySelectorAll('#fuelTable tbody tr');
                
                rows.forEach(row => {{
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(filter) ? '' : 'none';
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    with open("index.html", "w") as f:
        f.write(html_template)

if __name__ == "__main__":
    preston_content = get_preston_prices()
    generate_webpage(preston_content)
