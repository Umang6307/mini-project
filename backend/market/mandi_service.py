"""
Mandi Market Intelligence Service
Tracks commodity rates across Karnal, Gharaunda, Panipat, Kurukshetra, Taraori.
Includes MSP parity, arrivals, price trends, and historical 7-day sparklines.
"""

import json
from pathlib import Path
from backend.config import Config
from backend.database import query_db, execute_db

def get_all_mandi_prices() -> list:
    prices = query_db("SELECT * FROM mandi_prices ORDER BY crop_name, mandi_name;")
    if not prices:
        # Load fallback from data/mandi_prices.json
        mandi_file = Config.DATA_DIR / 'mandi_prices.json'
        if mandi_file.exists():
            with open(mandi_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    return prices

def get_crop_mandi_analysis(crop_name: str = "Wheat") -> dict:
    prices = query_db("SELECT * FROM mandi_prices WHERE crop_name LIKE ?;", (f"%{crop_name}%",))
    if not prices:
        prices = get_all_mandi_prices()

    highest_price = max(prices, key=lambda x: x['modal_price']) if prices else None
    lowest_price = min(prices, key=lambda x: x['modal_price']) if prices else None
    avg_price = sum(x['modal_price'] for x in prices) / len(prices) if prices else 0

    return {
        "crop": crop_name,
        "markets_count": len(prices),
        "best_mandi": highest_price['mandi_name'] if highest_price else "Karnal",
        "best_price": highest_price['modal_price'] if highest_price else 0,
        "lowest_price": lowest_price['modal_price'] if lowest_price else 0,
        "average_modal_price": round(avg_price, 1),
        "msp": prices[0]['msp_price'] if prices else 2275,
        "rates": prices,
        "source_label": "Demo Market Data (Simulated APMC Feed)"
    }
