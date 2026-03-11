import os
import requests
import datetime

def get_access_token():
    # Grabs the secrets we stored in GitHub
    client_id = os.getenv('FUEL_CLIENT_ID')
    client_secret = os.getenv('FUEL_CLIENT_SECRET')
    
    auth_url = "https://identity.fuel-finder.service.gov.uk/connect/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'fuel_price_read'
    }
    
    try:
        response = requests.post(auth_url, data=payload, timeout=10)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        print(f"Auth failed: {e}")
        return None

def get_prices(token):
    if not token:
        return "<tr><td colspan='2' class='text-danger'>Authentication Failed</td></tr>"
    
    # Statutory API - Preston PR1 Area (5 mile radius)
    url = "https://www.developer.fuel-finder.service.gov.uk/api/v1/prices"
    params = {
        'postcode': 'PR1',
        'radius': '5'
    }
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        rows = ""
        # Find stations with Diesel and sort by price
        stations_with_diesel = []
        for s in data.get('stations', []):
            diesel_info = next((p for p in s.get('prices', []) if p['fuel_type'].lower() == 'diesel'), None)
            if diesel_info:
                stations_with_diesel.append({
                    'name': f"{s.get('brand', 'Ind')} {s.get('name', '')}",
                    'postcode': s.get('postcode', 'PR1'),
                    'price': diesel_info['price']
                })
        
        sorted_stations = sorted(stations_with_diesel, key=lambda x: x['price'])
        
        for s in sorted_stations[:10]:
            rows += f"<tr><td><span class='station-name'>{s['name']}</span><br><small class='text-muted'>{s['postcode']}</small></td>"
            rows += f"<td class='text-end'><span class='price-badge'>{s['price']}p</span></td></tr>"
        
        return rows if rows else "<tr><td colspan='2'>No diesel prices found in area.</td></tr>"
    except Exception as e:
        return f"<tr><td colspan='2' class='text-danger'>Data Error: {e}</td></tr>"

def generate_webpage(content):
    now = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preston Fuel</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f8f9fa; padding: 20px; font-family: sans-serif; }}
            .card {{ border: none; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); }}
            .price-badge {{ color: #198754; font-weight: bold; font-size: 1.1rem; }}
            .station-name {{ font-weight: 600; color: #333; }}
        </style>
    </head>
    <body>
        <div class="container mt-4" style="max-width: 500px;">
            <h2 class="text-center fw-bold">⛽ Preston Diesel</h2>
            <p class="text-center text-muted small">Statutory Live Data | Updated: {now}</p>
            <div class="card p-3">
                <table class="table align-middle">
                    <thead><tr><th>Station</th><th class="text-end">Price</th></tr></thead>
                    <tbody>{content}</tbody>
                </table>
            </div>
            <div class="text-center mt-3 text-muted small">
                Data provided via GOV.UK Fuel Finder Scheme.
            </div>
        </div>
    </body>
    </html>"""
    
    with open("index.html", "w") as f:
        f.write(html_template)

if __name__ == "__main__":
    access_token = get_access_token()
    price_content = get_prices(access_token)
    generate_webpage(price_content)
