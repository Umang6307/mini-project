"""
Unit Converter Utility for Agricultural Land Metrics in India
Standard Conversions:
- 1 Hectare = 2.47105 Acres
- 1 Acre = 0.404686 Hectares
- 1 Acre = 8 Kanal (Haryana / Punjab) -> 1 Hectare = 19.7684 Kanal
- 1 Acre = 1.6 Bigha (Pucca / Haryana) -> 1 Hectare = 3.95368 Bigha
- 1 Acre = 40 Guntha (Maharashtra / Gujarat / South) -> 1 Hectare = 98.842 Guntha
"""

UNIT_TO_HECTARES = {
    'hectare': 1.0,
    'hectares': 1.0,
    'ha': 1.0,
    'acre': 0.404686,
    'acres': 0.404686,
    'ac': 0.404686,
    'bigha': 0.2529285,  # 1 Hectare = 3.95368 Bigha
    'kanal': 0.0505857,  # 8 kanal = 1 acre
    'guntha': 0.0101171  # 40 guntha = 1 acre
}

def convert_to_hectares(area_value: float, unit_name: str) -> float:
    unit_clean = unit_name.strip().lower()
    factor = UNIT_TO_HECTARES.get(unit_clean, 1.0)
    return round(float(area_value) * factor, 4)

def convert_from_hectares(hectares: float, target_unit: str) -> float:
    unit_clean = target_unit.strip().lower()
    factor = UNIT_TO_HECTARES.get(unit_clean, 1.0)
    return round(float(hectares) / factor, 4)

def convert_all_units(area_value: float, source_unit: str) -> dict:
    ha = convert_to_hectares(area_value, source_unit)
    return {
        'hectare': round(ha, 4),
        'acre': round(ha / UNIT_TO_HECTARES['acre'], 3),
        'bigha': round(ha / UNIT_TO_HECTARES['bigha'], 2),
        'kanal': round(ha / UNIT_TO_HECTARES['kanal'], 2),
        'guntha': round(ha / UNIT_TO_HECTARES['guntha'], 2)
    }
