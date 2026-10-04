"""
Weather Service for Agro-Met Telemetry & 5-Day Forecasts
Provides live simulated sensors with realism and manual sensor trigger support.
"""

import json
import random
from pathlib import Path
from backend.config import Config
from backend.database import query_db, execute_db

def get_weather_data(field_id: int = 1) -> dict:
    weather_file = Config.DATA_DIR / 'weather.json'
    base_data = {}
    if weather_file.exists():
        with open(weather_file, 'r', encoding='utf-8') as f:
            base_data = json.load(f)

    # Fetch latest reading from SQL
    db_reading = query_db(
        "SELECT * FROM weather_readings WHERE field_id = ? ORDER BY recorded_at DESC LIMIT 1;",
        (field_id,),
        one=True
    )

    if db_reading:
        base_data['current']['temperature_c'] = db_reading['temperature_c']
        base_data['current']['humidity_pct'] = db_reading['humidity_pct']
        base_data['current']['leaf_wetness_pct'] = db_reading['leaf_wetness_pct']
        base_data['current']['rainfall_prob_pct'] = db_reading['rainfall_prob_pct']
        base_data['current']['wind_speed_kmh'] = db_reading['wind_speed_kmh']
        base_data['current']['wind_direction'] = db_reading['wind_direction']
        base_data['current']['et0_mm_day'] = db_reading['et0_evapotranspiration_mm']
        if db_reading['forecast_summary']:
            base_data['current']['condition'] = db_reading['forecast_summary']

    return base_data

def simulate_new_reading(field_id: int = 1) -> dict:
    current = get_weather_data(field_id)['current']
    # Add realistic minor fluctuation
    new_temp = round(max(15.0, min(42.0, current['temperature_c'] + random.uniform(-1.2, 1.2))), 1)
    new_humidity = round(max(30.0, min(95.0, current['humidity_pct'] + random.uniform(-3.5, 3.5))), 1)
    new_leaf_wet = round(max(5.0, min(90.0, current['leaf_wetness_pct'] + random.uniform(-4.0, 4.0))), 1)
    new_rain_prob = round(max(0.0, min(90.0, current['rainfall_prob_pct'] + random.uniform(-5.0, 5.0))), 0)
    new_wind = round(max(4.0, min(35.0, current['wind_speed_kmh'] + random.uniform(-1.5, 1.5))), 1)

    execute_db("""
        INSERT INTO weather_readings (field_id, station_name, temperature_c, humidity_pct, leaf_wetness_pct, rainfall_prob_pct, wind_speed_kmh, is_simulated)
        VALUES (?, 'Karnal Agri-Met Station', ?, ?, ?, ?, ?, 1);
    """, (field_id, new_temp, new_humidity, new_leaf_wet, new_rain_prob, new_wind))

    return get_weather_data(field_id)
