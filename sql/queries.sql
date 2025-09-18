-- Prix moyen par ville
SELECT city, AVG(price_shekels) AS avg_price
FROM yad2_listings
GROUP BY city
ORDER BY avg_price DESC;

-- Prix au m² par quartier
SELECT city, neighborhood, AVG(price_per_sqm) AS avg_ppsqm, COUNT(*) AS n
FROM yad2_listings
WHERE neighborhood IS NOT NULL
GROUP BY city, neighborhood
HAVING COUNT(*) >= 3
ORDER BY avg_ppsqm DESC;

-- Top 5 quartiers les plus chers (par prix au m²)
SELECT city, neighborhood, AVG(price_per_sqm) AS avg_ppsqm, COUNT(*) AS n
FROM yad2_listings
WHERE neighborhood IS NOT NULL
GROUP BY city, neighborhood
HAVING COUNT(*) >= 3
ORDER BY avg_ppsqm DESC
LIMIT 5;
