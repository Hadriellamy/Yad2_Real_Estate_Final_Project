import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PROCESSED = BASE_DIR / "data" / "processed" / "listings_clean.csv"
MODEL_PATH = BASE_DIR / "models" / "price_model.joblib"

st.set_page_config(page_title="Yad2 Real Estate — Dashboard", layout="wide")
st.title("🏠 Yad2 — Real Estate Dashboard")

@st.cache_data
def load_data():
    if DATA_PROCESSED.exists():
        return pd.read_csv(DATA_PROCESSED)
    st.warning("Cleaned file not found. Please run the cleaning step first.")
    return pd.DataFrame()

@st.cache_resource
def load_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return None

df = load_data()
model = load_model()

if not df.empty:
    # Filters
    with st.sidebar:
        st.header("Filters")
        cities = sorted(df["city"].dropna().unique().tolist())
        city_sel = st.multiselect("City", options=cities, default=cities[:3])

        min_rooms, max_rooms = float(df["rooms"].min()), float(df["rooms"].max())
        rooms_range = st.slider(
            "Rooms",
            min_value=min_rooms,
            max_value=max_rooms,
            value=(min_rooms, max_rooms),
            step=0.5
        )

        min_area, max_area = float(df["area_sqm"].min()), float(df["area_sqm"].max())
        area_range = st.slider(
            "Area (sqm)",
            min_value=min_area,
            max_value=max_area,
            value=(min_area, max_area)
        )

    f = df[df["city"].isin(city_sel)]
    f = f[(f["rooms"] >= rooms_range[0]) & (f["rooms"] <= rooms_range[1])]
    f = f[(f["area_sqm"] >= area_range[0]) & (f["area_sqm"] <= area_range[1])]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Listings", len(f))
    with c2:
        st.metric("Avg Price (₪)", int(f["price_shekels"].mean()) if len(f) else 0)
    with c3:
        st.metric("Avg Price per sqm (₪)", int(f["price_per_sqm"].mean()) if len(f) else 0)
    with c4:
        st.metric("Median Area (sqm)", int(f["area_sqm"].median()) if len(f) else 0)

    st.subheader("Price Histogram")
    st.bar_chart(f["price_shekels"])

    st.subheader("Area vs Price (scatter)")
    st.scatter_chart(f, x="area_sqm", y="price_shekels", size="rooms", color="city")

    st.subheader("Average Price by City (bar chart)")
    st.bar_chart(f.groupby("city")["price_shekels"].mean())

    st.divider()
    st.subheader("🔮 Price Prediction (saved model)")
    if model is None:
        st.info("No saved model. Run `python src/ml_train.py` to train it.")
    else:
        colA, colB, colC, colD = st.columns(4)
        with colA:
            area_in = st.number_input(
                "Area (sqm)",
                min_value=10.0,
                max_value=400.0,
                value=float(df["area_sqm"].median())
            )
        with colB:
            rooms_in = st.number_input(
                "Rooms",
                min_value=1.0,
                max_value=8.0,
                value=float(df["rooms"].median()),
                step=0.5
            )
        with colC:
            floor_in = st.number_input(
                "Floor",
                min_value=0,
                max_value=40,
                value=int(df["floor"].median())
            )
        with colD:
            city_in = st.selectbox("City", options=sorted(df["city"].dropna().unique().tolist()))

        if st.button("Predict"):
            X = pd.DataFrame([{
                "area_sqm": area_in,
                "rooms": rooms_in,
                "floor": floor_in,
                "city": city_in
            }])
            y_pred = model.predict(X)[0]
            st.success(f"Estimated price: ₪ {int(y_pred):,}")

else:
    st.stop()

st.caption("⚠️ Results depend on available data and do not constitute financial advice.")
