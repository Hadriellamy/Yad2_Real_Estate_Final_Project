.PHONY: help setup install run clean scrape clean_data train refresh

PY?=python3
PIP?=$(PY) -m pip
VENV=.venv
ACTIVATE=. $(VENV)/bin/activate

# Params for scraping (override on command line)
QUERY?=תל אביב
PAGES?=3
OUT?=data/raw/yad2_scraped_pagination.csv

help:
	@echo "Common targets:"
	@echo "  make install      -> create venv & install deps"
	@echo "  make run          -> run Streamlit dashboard"
	@echo "  make scrape       -> scrape Yad2 (use QUERY=... PAGES=... OUT=...)"
	@echo "  make clean_data   -> clean the raw CSV into data/processed/listings_clean.csv"
	@echo "  make train        -> train/retrain the price model"
	@echo "  make refresh      -> scrape -> clean -> train in one go"
	@echo "  make clean        -> remove venv and pycache"

setup:
	$(PY) -m venv $(VENV)

install: setup
	$(ACTIVATE) && $(PIP) install -U pip
	$(ACTIVATE) && $(PIP) install -r requirements.txt

run:
	$(ACTIVATE) && $(PY) -m streamlit run dashboard/streamlit_app.py

scrape:
	$(ACTIVATE) && $(PY) src/scrape_yad2.py --query "$(QUERY)" --pages $(PAGES) --out $(OUT)

clean_data:
	$(ACTIVATE) && $(PY) src/clean_listings.py

train:
	$(ACTIVATE) && $(PY) src/ml_train.py

refresh: scrape clean_data train

clean:
	rm -rf $(VENV) __pycache__ **/__pycache__
