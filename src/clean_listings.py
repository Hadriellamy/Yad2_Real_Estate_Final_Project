# src/clean_listings.py
import re
from pathlib import Path
import numpy as np
import pandas as pd
from config import DATA_RAW, DATA_PROCESSED

RAW = Path(DATA_RAW)
OUT = Path(DATA_PROCESSED)

# ===================== Regex robustes =====================
RE_NUM_ANY   = re.compile(r'(\d[\d,.\s]{3,})')                     # nombres "grands"
RE_PRICE_ANY = re.compile(r'(?:₪|\u20AA|ש\"ח|ש״ח)\s*([\d,.\s]{3,})') # ₪ / ש"ח / ש״ח
RE_ROOMS     = re.compile(r'(\d+(?:\.\d+)?)\s*חדר', re.UNICODE)
RE_AREA      = re.compile(r'(\d+(?:\.\d+)?)\s*(?:\"|״)?\s*מ', re.UNICODE)
RE_FLOOR     = re.compile(r'קומה\s*(\d+)', re.UNICODE)

# seuil large pour écarter le "bruit"
PRICE_MIN = 50_000

# ===================== Helpers =====================
def to_float(s):
    """Convertit une chaîne (avec séparateurs) en float; NaN si impossible."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return np.nan
    s = str(s).replace('\u200f','').replace('\u202c','').strip()
    # homogénéiser: retirer espaces, puis virer séparateurs usuels
    s = s.replace(' ', '')
    # si on a à la fois '.' et ',' on retire les deux (on suppose séparation visuelle)
    if s.count(',') > 0 and s.count('.') > 0:
        s = s.replace(',', '').replace('.', '')
    else:
        s = s.replace(',', '')
    # dernière passe: garder chiffres/point
    s2 = re.sub(r'[^\d.]', '', s)
    try:
        return float(s2) if s2 else np.nan
    except:
        return np.nan

def extract_first_num(s):
    """Retourne un nombre trouvé dans la chaîne, en priorisant un motif de prix."""
    s = '' if s is None else str(s)
    m = RE_PRICE_ANY.search(s)
    if m:
        return to_float(m.group(1))
    m2 = RE_NUM_ANY.search(s)
    if m2:
        return to_float(m2.group(1))
    return np.nan

def parse_city_from_location(s):
    """Essaye d’extraire la ville depuis 'location' ('... , חולון' -> חולון)."""
    if not isinstance(s, str) or not s.strip():
        return "Unknown", None
    parts = [x.strip() for x in re.split(r'\s*[-/]\s*', s) if x.strip()]
    city  = parts[0] if parts else s.strip()
    neigh = parts[1] if len(parts) > 1 else None
    return city or "Unknown", neigh

def keep_city_only(s):
    """Garde seulement la ville (souvent le dernier segment après virgule)."""
    if not isinstance(s, str):
        return "Unknown"
    parts = [x.strip() for x in s.split(",") if x.strip()]
    return (parts[-1] if parts else s.strip()) or "Unknown"

def impute_series_num(s: pd.Series, default_val: float) -> pd.Series:
    s = pd.to_numeric(s, errors='coerce')
    if s.isna().all():
        return s.fillna(default_val)
    return s.fillna(s.median())

# ===================== Chargement =====================
if not RAW.exists():
    raise SystemExit(f"❌ Introuvable: {RAW} (lance d’abord le scraping).")

df = pd.read_csv(RAW)

# Colonnes minimales attendues par le projet / dashboard
for c in ["title", "price_shekels", "location", "details", "tags", "image_url", "url"]:
    if c not in df.columns:
        df[c] = np.nan

# ===================== Prix =====================
# Si price_shekels inexploitable, on le reconstruit depuis price/details/title/tags
price = pd.to_numeric(df.get("price_shekels"), errors="coerce")

if price.isna().all():
    sources = [c for c in ["price", "details", "title", "tags", "price_shekels"] if c in df.columns]
    vals = []
    for _, row in df.iterrows():
        val = np.nan
        for col in sources:
            v = row.get(col, "")
            val = extract_first_num(v)
            if not np.isnan(val):
                break
        vals.append(val)
    price = pd.Series(vals, index=df.index)

df["price_shekels"] = price

# ===================== Rooms / Area / Floor =====================
# Créer les colonnes au besoin
for c in ["rooms", "area_sqm", "floor", "city", "neighborhood"]:
    if c not in df.columns:
        df[c] = np.nan

# extractions via str.extract -> séries temporaires (évite warnings dtype)
def extract_into(col_target, regex, candidates=("tags","details","title")):
    mask = df[col_target].isna()
    for cand in (col_target,) + tuple(c for c in candidates if c in df.columns):
        if mask.sum() == 0:
            break
        if cand in df.columns:
            tmp = df.loc[mask, cand].astype(str).str.extract(regex, expand=False)
            # convertir uniquement ce qu’on va assigner
            tmp_num = pd.to_numeric(tmp, errors="coerce")
            df.loc[mask, col_target] = tmp_num
            mask = df[col_target].isna()

extract_into("rooms", RE_ROOMS)
extract_into("area_sqm", RE_AREA)
extract_into("floor", RE_FLOOR)

# ===================== City depuis location =====================
if df["city"].isna().any() or (df["city"].astype(str).str.strip() == "").any():
    cities, neighs = [], []
    for loc in df["location"].fillna(""):
        c, n = parse_city_from_location(loc)
        cities.append(c)
        neighs.append(n)
    df["city"] = df["city"].fillna(pd.Series(cities, index=df.index))
    df["neighborhood"] = df["neighborhood"].fillna(pd.Series(neighs, index=df.index))

# Nettoie la ville (gardez seulement la ville finale; enlève types de biens courants)
df["city"] = df["city"].apply(keep_city_only)
PROPERTY_WORDS = {"דירה", "דירת גן", "בית פרטי", "פנטהאוז", "גג", "קוטג"}
df["city"] = df["city"].apply(lambda s: "Unknown" if s in PROPERTY_WORDS else s)

# ===================== Conversions / filtrage =====================
for c in ["price_shekels", "rooms", "area_sqm", "floor"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# Garder lignes avec prix plausible
df = df[pd.to_numeric(df["price_shekels"], errors="coerce").notna()].copy()
df = df[df["price_shekels"] >= PRICE_MIN]

# Imputations simples
df["rooms"]    = impute_series_num(df["rooms"], 3.0)
df["area_sqm"] = impute_series_num(df["area_sqm"], 70.0)
df["floor"]    = impute_series_num(df["floor"], 2.0)
df["city"]     = df["city"].astype(str).replace({"nan": "Unknown", "": "Unknown"}).fillna("Unknown")

# ===================== price_per_sqm (💥 clé du dashboard) =====================
df["price_per_sqm"] = np.where(
    (df["area_sqm"] > 0) & df["price_shekels"].notna(),
    df["price_shekels"] / df["area_sqm"],
    np.nan
)

# ===================== Sauvegarde =====================
OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f"✅ Clean done. Saved {len(df)} rows to {OUT}")
