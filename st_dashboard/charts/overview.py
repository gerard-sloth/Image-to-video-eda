import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _stacked_area(df_long, x_col, y_col, color_col, percent, title, y_title):
    fig = px.area(
        df_long,
        x=x_col,
        y=y_col,
        color=color_col,
        groupnorm="percent" if percent else None,
        title=title,
    )
    fig.update_layout(
        legend_title_text=color_col,
        yaxis_title="Percent" if percent else y_title,
        xaxis_title="Week",
        margin=dict(l=40, r=20, t=50, b=40),
    )
    fig.update_yaxes(ticksuffix="%" if percent else None)
    return fig


def weekly_counts(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    return (
        df.groupby(["week_start", group_col])
        .size()
        .reset_index(name="count")
    )


def weekly_costs(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    return (
        df.groupby(["week_start", group_col])["default_cost"]
        .sum()
        .reset_index(name="cost")
    )


def requests_over_time(df: pd.DataFrame, group_col: str, percent: bool):
    df_long = weekly_counts(df, group_col)
    return _stacked_area(
        df_long,
        x_col="week_start",
        y_col="count",
        color_col=group_col,
        percent=percent,
        title="Requests Over Time",
        y_title="Jobs",
    )


def cost_over_time(df: pd.DataFrame, group_col: str, percent: bool):
    df_long = weekly_costs(df, group_col)
    return _stacked_area(
        df_long,
        x_col="week_start",
        y_col="cost",
        color_col=group_col,
        percent=percent,
        title="Cost Over Time",
        y_title="Total Cost",
    )


def jobs_and_cost_bar(df: pd.DataFrame, group_col: str):
    counts = df[group_col].value_counts()
    total_cost = df.groupby(group_col)["default_cost"].sum().reindex(counts.index)

    x = counts.index.tolist()
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Jobs", x=x, y=counts.values, marker_color="#4E79A7"))
    fig.add_trace(go.Bar(name="Total Cost", x=x, y=total_cost.values, marker_color="#E15759"))
    fig.update_layout(
        barmode="group",
        title="Jobs and Total Cost per Model Type (sorted by jobs)",
        xaxis_title="Model Type",
        yaxis_title="Value",
        margin=dict(l=40, r=20, t=50, b=80),
    )
    fig.update_xaxes(tickfont=dict(size=14))
    fig.update_yaxes(tickfont=dict(size=14), title_font=dict(size=14))
    return fig
