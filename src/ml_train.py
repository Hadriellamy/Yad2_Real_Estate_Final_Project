import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.dummy import DummyRegressor
import joblib
from config import DATA_PROCESSED, MODELS_DIR, REPORTS_DIR

def rmse(y_true, y_pred):
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

def load_data():
    df = pd.read_csv(DATA_PROCESSED)
    # Colonnes minimales
    needed = ["price_shekels", "rooms", "area_sqm", "floor", "city"]
    for c in needed:
        if c not in df.columns:
            df[c] = np.nan

    # Types
    for c in ["price_shekels", "rooms", "area_sqm", "floor"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["price_shekels"]).copy()

    # Imputations
    for c in ["rooms", "area_sqm", "floor"]:
        if df[c].isna().all():
            defaults = {"rooms": 3.0, "area_sqm": 70.0, "floor": 2.0}
            df[c] = defaults[c]
        else:
            df[c] = df[c].fillna(df[c].median())

    df["city"] = df["city"].astype(str).replace({"": "Unknown", "nan": "Unknown"}).fillna("Unknown")

    X = df[["rooms", "area_sqm", "floor", "city"]].copy()
    y = df["price_shekels"].copy()
    return df, X, y

def build_pipeline(kind="rf"):
    numeric = ["rooms", "area_sqm", "floor"]
    cat = ["city"]
    pre = ColumnTransformer(
        [("num", StandardScaler(), numeric),
         ("cat", OneHotEncoder(handle_unknown="ignore"), cat)]
    )

    if kind == "lr":
        est = LinearRegression()
    elif kind == "rf":
        est = RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=42)
    else:
        est = DummyRegressor(strategy="median")

    return Pipeline([("pre", pre), ("est", est)])

def main():
    df, X, y = load_data()
    n = len(df)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    metrics = {}

    if n < 10:
        # Jeu très petit: entraîne un modèle baseline (médiane) sur tout
        print(f"⚠️ Dataset petit (n={n}). Utilisation d'un modèle baseline.")
        base = build_pipeline("base")
        base.fit(X, y)
        pred = base.predict(X)
        metrics["baseline"] = {"rmse": rmse(y, pred), "r2": float(r2_score(y, pred)) if n > 1 else 0.0}
        best = ("baseline", base)
    else:
        # Split robuste: garantit au moins 1 échantillon test
        test_size = 0.2 if n >= 50 else max(0.1, min(0.2, 1.0 / max(n,1)))
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=test_size, random_state=42)

        lr = build_pipeline("lr")
        rf = build_pipeline("rf")

        lr.fit(X_tr, y_tr); p_lr = lr.predict(X_te)
        rf.fit(X_tr, y_tr); p_rf = rf.predict(X_te)

        metrics["linear_regression"] = {"rmse": rmse(y_te, p_lr), "r2": float(r2_score(y_te, p_lr))}
        metrics["random_forest"] = {"rmse": rmse(y_te, p_rf), "r2": float(r2_score(y_te, p_rf))}

        best_name = min(metrics, key=lambda k: metrics[k]["rmse"])
        best = (best_name, lr if best_name == "linear_regression" else rf)

    # Sauvegardes
    name, model = best
    joblib.dump(model, MODELS_DIR / "price_model.joblib")
    (REPORTS_DIR / "training_metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"✅ Training done. Best: {name}. Model saved to {MODELS_DIR/'price_model.joblib'}")

if __name__ == "__main__":
    main()
