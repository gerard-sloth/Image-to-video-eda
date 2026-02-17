import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

from st_dashboard.data.transforms import build_family_palette


def _label_top_n(df_long, label_col, value_col, top_n):
    totals = df_long.groupby(label_col)[value_col].sum().sort_values(ascending=False)
    top_titles = totals.head(top_n).index.tolist()
    df_long = df_long.copy()
    df_long["label"] = df_long[label_col].where(df_long[label_col].isin(top_titles), "Other")
    return df_long, top_titles


def _stacked_area(df_long, x_col, y_col, label_col, percent, title, y_title):
    totals = df_long.groupby(label_col)[y_col].sum().to_dict()
    palette_map = build_family_palette(df_long[label_col].unique(), totals=totals)
    if "Other" in df_long[label_col].unique():
        palette_map.setdefault("Other", "#BAB0AC")

    fig = px.area(
        df_long,
        x=x_col,
        y=y_col,
        color=label_col,
        groupnorm="percent" if percent else None,
        color_discrete_map=palette_map,
        title=title,
    )
    fig.update_layout(
        legend_title_text=label_col,
        yaxis_title="Percent" if percent else y_title,
        xaxis_title="Week",
        margin=dict(l=40, r=20, t=50, b=40),
    )
    fig.update_yaxes(ticksuffix="%" if percent else None)
    return fig


def usage_over_time(df_sub, top_n=8, percent=False):
    df_long = (
        df_sub.groupby(["week_start", "model_title_extracted"])
        .size()
        .reset_index(name="count")
    )
    df_long, _ = _label_top_n(df_long, "model_title_extracted", "count", top_n)
    df_long = df_long.groupby(["week_start", "label"])["count"].sum().reset_index()
    return _stacked_area(
        df_long,
        x_col="week_start",
        y_col="count",
        label_col="label",
        percent=percent,
        title="Generation Usage Over Time",
        y_title="Jobs",
    )


def cost_over_time(df_sub, top_n=8, percent=False):
    df_long = (
        df_sub.groupby(["week_start", "model_title_extracted"])["default_cost"]
        .sum()
        .reset_index(name="cost")
    )
    df_long, _ = _label_top_n(df_long, "model_title_extracted", "cost", top_n)
    df_long = df_long.groupby(["week_start", "label"])["cost"].sum().reset_index()
    return _stacked_area(
        df_long,
        x_col="week_start",
        y_col="cost",
        label_col="label",
        percent=percent,
        title="Cost Over Time",
        y_title="Total Cost",
    )


def quality_boxplot(df_sub, top_titles):
    df_plot = df_sub[df_sub["model_title_extracted"].isin(top_titles)].copy()
    df_plot = df_plot.dropna(subset=["quality_score"])
    if df_plot.empty:
        return None

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.boxplot(
        data=df_plot,
        x="model_title_extracted",
        y="quality_score",
        showfliers=False,
        ax=ax,
    )
    ax.set_title("Quality score by model")
    ax.set_xlabel("Model")
    ax.set_ylabel("Quality score")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    return fig


def quality_kde(df_sub, top_titles):
    df_plot = df_sub[df_sub["model_title_extracted"].isin(top_titles)].copy()
    df_plot = df_plot.dropna(subset=["quality_score"])
    if df_plot.empty:
        return None

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.kdeplot(
        data=df_plot,
        x="quality_score",
        hue="model_title_extracted",
        common_norm=False,
        fill=True,
        alpha=0.25,
        ax=ax,
    )
    ax.set_title("Quality score distribution")
    ax.set_xlabel("Quality score")
    ax.grid(alpha=0.4)
    plt.tight_layout()
    return fig


def download_rate_bar(df_sub, top_titles):
    df_plot = df_sub[df_sub["model_title_extracted"].isin(top_titles)].copy()
    if df_plot.empty:
        return None
    download_rate = (
        df_plot.groupby("model_title_extracted")["was_downloaded"]
        .mean()
        .sort_values(ascending=False)
    )
    fig, ax = plt.subplots(figsize=(12, 4.5))
    sns.barplot(x=download_rate.index, y=download_rate.values, color="#4E79A7", ax=ax)
    ax.set_title("Download rate by model")
    ax.set_xlabel("Model")
    ax.set_ylabel("Download rate")
    plt.xticks(rotation=35, ha="right")
    plt.grid(alpha=0.4)
    plt.tight_layout()
    return fig


def avg_cost_bar(df_sub, top_titles):
    df_plot = df_sub[df_sub["model_title_extracted"].isin(top_titles)].copy()
    if df_plot.empty:
        return None
    avg_cost = (
        df_plot.groupby("model_title_extracted")["default_cost"]
        .mean()
        .sort_values(ascending=False)
    )
    totals = df_plot.groupby("model_title_extracted")["default_cost"].sum().to_dict()
    palette_map = build_family_palette(avg_cost.index.tolist(), totals=totals)
    ordered_labels = avg_cost.index.tolist()
    colors = [palette_map.get(label, "#4E79A7") for label in ordered_labels]

    fig = go.Figure(
        go.Bar(
            x=avg_cost.values,
            y=ordered_labels,
            orientation="h",
            marker_color=colors,
            showlegend=False,
        )
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        title="Average default cost by model",
        xaxis_title="Average Cost",
        yaxis_title="Model",
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig


def weekly_avg_cost_line(df_sub, top_titles):
    df_plot = df_sub[df_sub["model_title_extracted"].isin(top_titles)].copy()
    if df_plot.empty:
        return None
    df_ts = (
        df_plot.groupby(["week_start", "model_title_extracted"])["default_cost"]
        .mean()
        .reset_index(name="avg_cost")
    )
    totals = df_plot.groupby("model_title_extracted")["default_cost"].sum().to_dict()
    palette_map = build_family_palette(df_plot["model_title_extracted"].unique(), totals=totals)

    fig = px.line(
        df_ts,
        x="week_start",
        y="avg_cost",
        color="model_title_extracted",
        color_discrete_map=palette_map,
        title="Weekly average cost",
    )
    fig.update_layout(xaxis_title="Week", yaxis_title="Average Cost")
    return fig


def scatter_quality_cost(df_sub, top_titles):
    df_plot = df_sub[df_sub["model_title_extracted"].isin(top_titles)].copy()
    summary = (
        df_plot.groupby("model_title_extracted")
        .agg(
            n=("quality_score", "size"),
            avg_score=("quality_score", "mean"),
            avg_cost=("default_cost", "mean"),
            download_rate=("was_downloaded", "mean"),
        )
        .reset_index()
    )
    if summary.empty:
        return None

    totals = df_plot.groupby("model_title_extracted")["default_cost"].sum().to_dict()
    palette_map = build_family_palette(summary["model_title_extracted"].unique(), totals=totals)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    ax1, ax2 = axes

    for _, row in summary.iterrows():
        color = palette_map.get(row["model_title_extracted"], "#4E79A7")
        size = max(40, np.sqrt(row["n"]) * 20)
        ax1.scatter(
            row["avg_score"],
            row["avg_cost"],
            s=size,
            color=color,
            alpha=0.6,
            edgecolors="white",
            linewidths=0.5,
        )
        ax2.scatter(
            row["download_rate"],
            row["avg_cost"],
            s=size,
            color=color,
            alpha=0.6,
            edgecolors="white",
            linewidths=0.5,
        )

    ax1.set_title("Avg Score vs Avg Cost")
    ax1.set_xlabel("Average Quality Score")
    ax1.set_ylabel("Average Cost")
    ax1.grid(alpha=0.4)

    ax2.set_title("Download Rate vs Avg Cost")
    ax2.set_xlabel("Download Rate")
    ax2.grid(alpha=0.4)

    plt.tight_layout()
    return fig
