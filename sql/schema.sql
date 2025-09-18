-- Créez la base manuellement si besoin: CREATE DATABASE real_estate;
CREATE TABLE IF NOT EXISTS yad2_listings (
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
