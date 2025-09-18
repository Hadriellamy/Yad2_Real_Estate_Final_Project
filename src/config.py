from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_RAW = BASE_DIR / "data" / "raw" / "yad2_scraped_pagination.csv"
DATA_PROCESSED = BASE_DIR / "data" / "processed" / "listings_clean.csv"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

# DB
DATABASE_URL = os.getenv("DATABASE_URL")  # postgresql+psycopg2://USER:PASSWORD@HOST:PORT/real_estate
TABLE_NAME = "yad2_listings"
