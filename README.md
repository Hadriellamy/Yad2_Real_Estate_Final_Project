# 🏗 Final Year Project — Yad2 Real Estate Data(Israel)

Complete project **scraping → cleaning → database → statistics → Machine Learning → Dashboard → deployment**.

## 🔧 Quick installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```


## 📁 Structure

```
yad2_real_estate_project/
├─ data/
│  ├─ raw/                 # raw data(scrapées)
│  └─ processed/           # cleaned data(listings_clean.csv)
├─ models/                 # saved ML models (joblib)
├─ reports/                # stats & metrics
├─ dashboard/              # app Streamlit
├─ notebooks/              # analysis notebook
├─ sql/                    # schema & SQL queries
└─ src/                    # scripts Python (scraping, cleaning, DB, stats, ML)
```



## 🌐 Scraping for Yad2 data

> ⚠️ Respect the CGU/robots.txt, add breaks, do not overload the site, use scraping for educational purposes only.

```bash
python src/scrape_yad2.py --query "תל אביב" --pages 3 --out data/raw/yad2_scraped_pagination.csv
```

## 🗄️ Database (PostgreSQL)

- Create a base `real_estate` if necessary.
- The script `src/load_to_postgres.py` create the table `yad2_listings` and loads `listings_clean.csv`.
- Examples of queries are in `sql/queries.sql`.

## 📊 Dashboard

- `dashboard/streamlit_app.py` read `data/processed/listings_clean.csv` and the **modèle** if  exist.
- Filters: **city, nb of rooms, area**.
- Charts: price histogram, scatter area vs price, bar chart average price by city.
- Predictor: Enter area / rooms / floor / city→ **estimated price**.

## 📓 Notebook

- `notebooks/analysis.ipynb`: descriptive statistics, t-test (Tel Aviv vs Jerusalem), simple linear regression.


## 🚀 Quickstart

### Option A — Local environment (recommended)
```bash
make install
make run
# puis ouvrez http://localhost:8501
```

> If you don't have  `make` :  
> macOS: `xcode-select --install` • Windows: use `Git Bash` or run manually:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
python -m streamlit run dashboard/streamlit_app.py
```

### Option B — Docker
```bash
docker build -t yad2-dashboard .
docker run --rm -p 8501:8501 yad2-dashboard
# ou
docker compose up --build
```

### ⚠️ NOT TO COMMIT
The `.venv/` folder (local virtual environment) must **not** be versioned.
If it already exists in the project, delete it before creating a new venv:
```bash
rm -rf .venv
```


## 🔄 Mettre à jour avec vos propres données Yad2

### 1) Scraper Yad2 (opens Chrome automatically)
> Prerequisites: Google Chrome installed. Manually complete the captcha if prompted, then return to the terminal.
```bash
make install  # First time
make scrape QUERY="תל אביב" PAGES=3 OUT=data/raw/yad2_scraped_pagination.csv
```

### 2) Clean the data
```bash
make clean_data
```

### 3) (Optional) Retrain the model
```bash
make train
```

### 4) Launch the dashboard
```bash
make run
# http://localhost:8501
```

> All-in-one:
```bash
make refresh QUERY="ירושלים" PAGES=5
```
