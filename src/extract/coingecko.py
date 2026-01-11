import requests
import src.utils.config as config

BASE_URL = "https://api.coingecko.com/api/v3/coins/markets"

headers = {"accept": "application/json", "x-cg-demo-api-key": config.API_KEY}

def market_snapshot(vs_currency="usd", order="market_cap_desc", per_page=50, page=1, sparkline="false"):
    
    params = {
        "vs_currency": vs_currency,
        "order": order,
        "per_page": per_page,
        "page": page,
        "sparkline": sparkline,
        "price_change_percentage": "24h",
    }

    r= requests
response = requests.get(url, headers=headers, params=params, timeout=30)
response.raise_for_status()
print(response.json())
