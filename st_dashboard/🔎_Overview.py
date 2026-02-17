import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from st_dashboard.data.loader import load_data
from st_dashboard.charts.overview import (
    requests_over_time,
    cost_over_time,
    jobs_and_cost_bar,
)

st.set_page_config(page_title="🔎 Overview", layout="wide")

css_path = Path(__file__).parent / "theme" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

logo_path = Path(__file__).parent / "assets" / "studio-jadu.png"
if logo_path.exists():
    st.image(str(logo_path), use_container_width=False)

st.header("Overview")

try:
    with st.spinner("Loading data..."):
        df = load_data()
except Exception as exc:
    st.error(f"Failed to load data from MongoDB: {exc}")
    st.stop()

if df.empty:
    st.warning("No data returned from MongoDB.")
    st.stop()

min_date = df["created_at"].min().date()
max_date = df["created_at"].max().date()

st.sidebar.subheader("Filters")
start_date, end_date = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

mode = st.sidebar.radio("Stacked area mode", ["Absolute", "Percent"], index=0)
percent = mode == "Percent"

model_types = sorted(df["model_type_agg"].dropna().unique().tolist())
selected_types = st.sidebar.multiselect(
    "Model types",
    model_types,
    default=model_types,
)

mask = (df["created_at"].dt.date >= start_date) & (df["created_at"].dt.date <= end_date)
if selected_types:
    mask &= df["model_type_agg"].isin(selected_types)

filtered = df[mask].copy()

if filtered.empty:
    st.warning("No data for the selected filters.")
    st.stop()

st.subheader("Requests over time")
fig_requests = requests_over_time(filtered, group_col="model_type_agg", percent=percent)
st.plotly_chart(fig_requests, use_container_width=True)

st.subheader("Cost over time")
fig_cost = cost_over_time(filtered, group_col="model_type_agg", percent=percent)
st.plotly_chart(fig_cost, use_container_width=True)

st.subheader("Jobs and total cost by model type")
fig_bar = jobs_and_cost_bar(filtered, group_col="model_type_agg")
st.plotly_chart(fig_bar, use_container_width=True)
