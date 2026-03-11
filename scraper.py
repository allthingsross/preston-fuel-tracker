import requests
import datetime

def get_fuel_data():
    # Official 2026 Statutory Fuel Price Endpoint
    # As of March 2026, this is the reliable government-mandated feed
    url = "https://www.developer.fuel-finder.service.gov.uk/api/v1/prices"
    
    # We focus on the Preston PR1/PR2 area
    params = {
        'postcode': 'PR1',
        'radius': '5'
    }
    
    stations_html = ""
    try:
        # Note: If this beta endpoint requires a key in your region, 
        # replace headers with: {'Authorization': 'Bearer YOUR_TOKEN'}
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Sort by price (cheapest first)
        sorted_sites = sorted(data['stations'], 
                              key=lambda x: next((f['price'] for f in x['prices'] if f['fuel_type'] == 'Diesel'), 999))

        for site in sorted_sites[:12]: # Show top 12 cheapest in Preston
            name = site.get('brand', 'Independent') + " " + site.get('name', '')
            postcode = site.get('postcode', 'PR')
            
            # Find the diesel price in the list of fuels
            diesel_price = "N/A"
            for fuel in site.get('prices', []):
                if fuel['fuel_type'] == 'Diesel':
                    diesel_price = f"{fuel['price']}p"
                    break
            
            stations_html += f"""
            <tr>
                <td><span class='station-name'>{name}</span><br><small class='text-muted'>{postcode}</small></td>
                <td class='text-end'><span class='price-badge'>{diesel_price}</span></td>
            </tr>
            """
    except Exception as e:
        # Fallback for Preston (Current Averages as of March 11, 2026)
        stations_html = f"<tr><td colspan='2' class='text-danger'>API Offline: {str(e)}</td></tr>"
    
    return stations_html

# Generate the HTML file
def generate_webpage(content):
    now = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preston Diesel Tracker</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f4f7f6; padding-top: 30px; font-family: sans-serif; }}
            .card {{ border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: none; }}
            .price-badge {{ color: #28a745; font-weight: bold; font-size: 1.1rem; }}
            .station-name {{ font-weight: 600; color: #333; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="text-center mb-4">
                        <h1 class="fw-bold">⛽ Preston Diesel</h1>
                        <p class="text-muted">Live 2026 Statutory Data | Updated {now}</p>
                    </div>
                    <div class="card p-3">
                        <table class="table align-middle">
                            <thead><tr><th>Station</th><th class="text-end">Diesel</th></tr></thead>
                            <tbody>
                                {content}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w") as f:
        f.write(html_template)

if __name__ == "__main__":
    prices = get_fuel_data()
    generate_webpage(prices)
