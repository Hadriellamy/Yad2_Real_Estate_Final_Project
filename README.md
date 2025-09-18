# 🏗 Projet de Fin d'Étude — Données Immobilier Yad2 (Israel)

Projet complet **scraping → nettoyage → base de données → stats → ML → dashboard → déploiement**.

## 🔧 Installation rapide

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```


## 📁 Structure

```
yad2_real_estate_project/
├─ data/
│  ├─ raw/                 # données brutes (scrapées)
│  └─ processed/           # données nettoyées (listings_clean.csv)
├─ models/                 # modèles ML enregistrés (joblib)
├─ reports/                # stats & métriques
├─ dashboard/              # app Streamlit
├─ notebooks/              # notebook d'analyse
├─ sql/                    # schéma & requêtes SQL
└─ src/                    # scripts Python (scraping, nettoyage, DB, stats, ML)
```



## 🌐 Scraping pour données Yad2

> ⚠️ Respectez les CGU/robots.txt, ajoutez des pauses, ne surchargez pas le site, utilisez le scraping à des fins pédagogiques uniquement.

```bash
python src/scrape_yad2.py --query "תל אביב" --pages 3 --out data/raw/yad2_scraped_pagination.csv
```

## 🗄️ Base de données (PostgreSQL)

- Créez une base `real_estate` si nécessaire.
- Le script `src/load_to_postgres.py` crée la table `yad2_listings` et charge `listings_clean.csv`.
- Des exemples de requêtes sont dans `sql/queries.sql`.

## 📊 Dashboard

- `dashboard/streamlit_app.py` lit `data/processed/listings_clean.csv` et le **modèle** s'il existe.
- Filtres: **ville, nb de pièces, surface**.
- Graphiques: histogramme des prix, scatter surface vs prix, bar chart prix moyen par ville.
- Prédicteur: saisissez surface / pièces / étage / ville → **prix estimé**.

## 📓 Notebook

- `notebooks/analysis.ipynb`: stats descriptives, t-test (Tel Aviv vs Jérusalem), régression linéaire simple.





## 🚀 Quickstart

### Option A — Environnement local (recommandé)
```bash
make install
make run
# puis ouvrez http://localhost:8501
```

> Si vous n'avez pas `make` :  
> macOS: `xcode-select --install` • Windows: utilisez `Git Bash` ou exécutez manuellement:
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

### ⚠️ À NE PAS COMMIT
Le dossier `.venv/` (environnement virtuel local) ne doit **pas** être versionné.  
S'il existe déjà dans le projet, supprimez-le avant de créer un nouveau venv :
```bash
rm -rf .venv
```


## 🔄 Mettre à jour avec vos propres données Yad2

### 1) Scraper Yad2 (ouvre Chrome automatiquement)
> Prérequis: Google Chrome installé. Faites passer manuellement le captcha si demandé, puis revenez au terminal.
```bash
make install  # première fois
make scrape QUERY="תל אביב" PAGES=3 OUT=data/raw/yad2_scraped_pagination.csv
```

### 2) Nettoyer les données
```bash
make clean_data
```

### 3) (Optionnel) Réentraîner le modèle
```bash
make train
```

### 4) Lancer le dashboard
```bash
make run
# http://localhost:8501
```

> Tout-en-un :
```bash
make refresh QUERY="ירושלים" PAGES=5
```
