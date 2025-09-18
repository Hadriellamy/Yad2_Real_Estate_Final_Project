import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text
from config import DATA_PROCESSED, DATABASE_URL, TABLE_NAME

def main():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL manquant (.env)")

    engine = create_engine(DATABASE_URL, future=True)
    df = pd.read_csv(DATA_PROCESSED)

    # Créer table si nécessaire (types simples)
    ddl = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id SERIAL PRIMARY KEY,
        title TEXT,
        city TEXT,
        neighborhood TEXT,
        rooms FLOAT,
        floor INT,
        area_sqm FLOAT,
        price_shekels BIGINT,
        price_per_sqm FLOAT,
        url TEXT
    );
    '''
    with engine.begin() as conn:
        conn.execute(text(ddl))

    # Charger
    df[["title","city","neighborhood","rooms","floor","area_sqm","price_shekels","price_per_sqm","url"]]        .to_sql(TABLE_NAME, engine, if_exists="append", index=False)

    print(f"Import OK → table {TABLE_NAME}, {len(df)} lignes ajoutées.")

if __name__ == "__main__":
    main()
