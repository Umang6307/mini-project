import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def resolve_db_path():
    db_env = os.environ.get('DATABASE_PATH', '').strip()
    if not db_env or db_env in ['database', 'database/']:
        return str(BASE_DIR / 'database' / 'smart_crop.db')
    p = Path(db_env)
    if p.is_dir() or (BASE_DIR / p).is_dir():
        return str(p / 'smart_crop.db') if p.is_absolute() else str(BASE_DIR / p / 'smart_crop.db')
    return str(p if p.is_absolute() else BASE_DIR / p)

class Config:
    PORT = int(os.environ.get('PORT', 3000))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart_crop_advisory_secret_2026_dev')
    DATABASE_PATH = resolve_db_path()
    SCHEMA_PATH = BASE_DIR / 'database' / 'schema.sql'
    SEED_PATH = BASE_DIR / 'database' / 'seed.sql'
    DEMO_DATA_PATH = BASE_DIR / 'database' / 'demo_data.sql'
    DATA_DIR = BASE_DIR / 'data'
    GENERATED_DIR = BASE_DIR / 'generated' / 'insurance'
    UPLOAD_DIR = BASE_DIR / 'data' / 'uploads'
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()

    # Ensure directories exist
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (BASE_DIR / 'database').mkdir(parents=True, exist_ok=True)
