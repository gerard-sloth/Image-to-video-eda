import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

st.set_page_config(page_title="🛠️ Task Breakdown", layout="wide")

from st_dashboard.data.loader import load_data
from st_dashboard.data.constants import MAIN_MODEL_TYPES, DEFAULT_TOP_N
from st_dashboard.charts.task_breakdown import (
    usage_over_time,
    cost_over_time,
    quality_boxplot,
    quality_kde,
    download_rate_bar,
    avg_cost_bar,
    weekly_avg_cost_line,
    scatter_quality_cost,
)

logo_path = Path(__file__).resolve().parents[1] / "assets" / "studio-jadu.png"
if logo_path.exists():
    st.image(str(logo_path), use_container_width=False)

st.header("Task Breakdown")
st.caption("Deep dive into a single task type, comparing model usage, cost, and quality signals.")

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

model_types = [t for t in MAIN_MODEL_TYPES if t in df["model_type"].unique()]
if not model_types:
    model_types = sorted(df["model_type"].dropna().unique().tolist())

default_index = model_types.index("i2i") if "i2i" in model_types else 0
selected_type = st.sidebar.selectbox("Task", model_types, index=default_index)

mode = st.sidebar.radio("Stacked area mode", ["Absolute", "Percent"], index=0)
percent = mode == "Percent"

top_n = st.sidebar.slider("Top N models", min_value=3, max_value=12, value=DEFAULT_TOP_N, step=1)

mask = (df["created_at"].dt.date >= start_date) & (df["created_at"].dt.date <= end_date)
mask &= df["model_type"] == selected_type

filtered = df[mask].copy()

if filtered.empty:
    st.warning("No data for the selected filters.")
    st.stop()

st.subheader(f"Generation usage over time ({selected_type})")
st.caption("Weekly job volume for top models within the selected task.")
fig_usage = usage_over_time(filtered, top_n=top_n, percent=percent)
st.plotly_chart(fig_usage, use_container_width=True)

st.subheader(f"Cost over time ({selected_type})")
st.caption("Weekly estimated cost for top models within the selected task.")
fig_cost = cost_over_time(filtered, top_n=top_n, percent=percent)
st.plotly_chart(fig_cost, use_container_width=True)

# Determine top titles for detailed plots
model_title_counts = filtered["model_title_extracted"].value_counts().head(top_n)
top_titles = model_title_counts.index.tolist()

st.subheader("Quality")
st.caption("Quality score distribution and download rates for the selected task.")
quality_available = filtered["quality_score"].notna().any()
if not quality_available:
    st.info("No quality scores available for this task type.")
else:
    col_q1, col_q2 = st.columns([1, 1])
    fig_box = quality_boxplot(filtered, top_titles)
    with col_q1:
        if fig_box is not None:
            st.pyplot(fig_box, use_container_width=True)
        else:
            st.info("No boxplot data.")

    fig_kde = quality_kde(filtered, top_titles)
    with col_q2:
        if fig_kde is not None:
            st.pyplot(fig_kde, use_container_width=True)
        else:
            st.info("No distribution data.")

    fig_download = download_rate_bar(filtered, top_titles)
    if fig_download is not None:
        st.pyplot(fig_download, use_container_width=True)
    else:
        st.info("No download rate data.")

st.subheader("Cost")
st.caption("Average model cost and weekly cost trends for the selected task.")
col_c1, col_c2 = st.columns(2)
fig_avg_cost = avg_cost_bar(filtered, top_titles)
with col_c1:
    if fig_avg_cost is not None:
        st.plotly_chart(fig_avg_cost, use_container_width=True)
    else:
        st.info("No cost bar data.")

fig_weekly_cost = weekly_avg_cost_line(filtered, top_titles)
with col_c2:
    if fig_weekly_cost is not None:
        st.plotly_chart(fig_weekly_cost, use_container_width=True)
    else:
        st.info("No weekly cost data.")

st.subheader("Quality vs Cost")
st.caption("Relationship between quality outcomes and average cost per model.")
fig_scatter = scatter_quality_cost(filtered, top_titles)
if fig_scatter is not None:
    st.pyplot(fig_scatter)
