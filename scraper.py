import requests
import datetime
import json

# Official 2026 Open Data links (Statutory mandate feeds)
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
            # Using a modern User-Agent to avoid 403 Forbidden errors
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, headers=headers, timeout=12)
            
            if response.status_code != 200:
                continue
                
            data = response.json()
            # Most feeds use a top-level 'stations' key
            stations_list = data.get('stations', [])
            
            for station in stations_list:
                pc = str(station.get('postcode', '')).upper().replace(" ", "")
                
                # Broad Preston filter: PR1, PR2, PR3, PR4, PR5
                if pc.startswith(('PR1', 'PR2', 'PR3', 'PR4', 'PR5')):
                    prices = station.get('prices', {})
                    
                    # 2026 Fuel Label Check: Looks for Diesel, B7, or Diesel_B7
                    # This captures Shell/BP who often omit the word 'Diesel'
                    d_price = prices.get('Diesel') or prices.get('B7') or prices.get('diesel')
                    
                    if d_price:
                        found_stations.append({
                            'brand': brand,
                            'name': station.get('name', 'Forecourt'),
                            'postcode': station.get('postcode', ''),
                            'price': float(d_price)
                        })
        except Exception as e:
            # Skip silent failures to keep the app running
            continue

    # Sort all Preston stations by cheapest diesel first
    found_stations.sort(key=lambda x: x['price'])

    if not found_stations:
        return "<tr><td colspan='2' class='text-center'>No live data found for Preston. API syncing...</td></tr>"

    for s in found_stations:
        html_rows += f"""
        <tr>
            <td><span class='station-name'>{s['brand']} {s['name']}</span><br>
                <small class='text-muted'>{s['postcode']}</small></td>
            <td class='text-end'><span class='price-badge'>{s['price']}p</span></td>
        </tr>"""
    
    return html_rows

def generate_webpage(content):
    now = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
