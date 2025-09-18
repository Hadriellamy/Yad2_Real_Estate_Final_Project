import json
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
from config import DATA_PROCESSED, REPORTS_DIR

def main():
    df = pd.read_csv(DATA_PROCESSED)

    # Descriptives
    desc = {
        "n": int(len(df)),
        "price_mean": float(df["price_shekels"].mean()),
        "price_median": float(df["price_shekels"].median()),
        "price_std": float(df["price_shekels"].std()),
        "ppsqm_mean": float(df["price_per_sqm"].mean()),
        "rooms_dist": df["rooms"].value_counts().sort_index().to_dict()
    }

    # T-test Tel Aviv vs Jerusalem (si présent)
    tv = df[df["city"].str.contains("Tel Aviv", case=False, na=False)]["price_shekels"]
    jr = df[df["city"].str.contains("Jerusalem", case=False, na=False)]["price_shekels"]
    ttest = None
    if len(tv) > 2 and len(jr) > 2:
        t_stat, p_val = stats.ttest_ind(tv, jr, equal_var=False)
        ttest = {"t_stat": float(t_stat), "p_value": float(p_val), "n_tel_aviv": int(len(tv)), "n_jerusalem": int(len(jr))}

    # Save
    Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)
    (Path(REPORTS_DIR) / "stats.json").write_text(json.dumps({"desc": desc, "t_test_telaviv_vs_jerusalem": ttest}, indent=2))

    print("Stats sauvegardées → reports/stats.json")
    print(json.dumps({"desc": desc, "t_test_telaviv_vs_jerusalem": ttest}, indent=2))

if __name__ == "__main__":
    main()
