import requests
import src.utils.config as config
from datetime import datetime, timezone

BASE_URL = "https://api.coingecko.com/api/v3/coins/markets"

headers = {"accept": "application/json", "x-cg-demo-api-key": config.API_KEY}

def fetch_market_snapshot(vs_currency="usd", order="market_cap_desc", per_page=50, page=1, sparkline="false"):
    
    params = {
        "vs_currency": vs_currency,
        "order": order,
        "per_page": per_page,
        "page": page,
        "sparkline": sparkline,
        "price_change_percentage": "24h",
    }

    r = requests.get(BASE_URL, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    snapshot_ts = datetime.now(timezone.utc).isoformat()
    rows = []

    for row in data:
        rows.append({
            "snapshot_ts": snapshot_ts,
            "asset_id": row.get("id"),
            "symbol": row.get("symbol"),
            "name": row.get("name"),
            "current_price": row.get("current_price"),
            "market_cap": row.get("market_cap"),
            "market_cap_rank": row.get("market_cap_rank"),
            "total_volume": row.get("total_volume"),
            "high_24h": row.get("high_24h"),
            "low_24h": row.get("low_24h"),
            "price_change_24h": row.get("price_change_24h"),
            "price_change_percentage_24h": row.get("price_change_percentage_24h"),
            "last_updated": row.get("last_updated"),
        })
    return rows

if __name__ == "__main__":
    rows = market_snapshot()
    print(rows[:2])
