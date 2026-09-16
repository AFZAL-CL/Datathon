from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard.utils.data import OUTCOME_COLORS, OUTCOMES

TEMPLATE = "plotly_white"


def _base(fig: go.Figure, height: int = 350) -> go.Figure:
    fig.update_layout(template=TEMPLATE, height=height, margin=dict(l=12, r=12, t=48, b=12), font=dict(family="Inter, sans-serif", color="#263538"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title_text="")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#e8eeeb")
    return fig


def outcome_distribution(df: pd.DataFrame) -> go.Figure:
    counts = df["Target"].value_counts().reindex(OUTCOMES, fill_value=0).rename_axis("Outcome").reset_index(name="Students")
    fig = px.bar(counts, x="Students", y="Outcome", orientation="h", color="Outcome", color_discrete_map=OUTCOME_COLORS, text="Students", title="Observed student outcomes")
    fig.update_traces(textposition="outside")
    return _base(fig, 300)


def dropout_by_dimension(df: pd.DataFrame, dimension: str, title: str, order: list[str] | None = None, top_n: int | None = None) -> go.Figure:
    if df.empty or dimension not in df:
        return go.Figure()
    table = df.groupby(dimension).agg(students=("Target", "size"), dropout=("Target", lambda x: (x == "Dropout").mean() * 100)).reset_index()
    if top_n:
        table = table.sort_values("students", ascending=False).head(top_n)
    table = table.sort_values("dropout")
    if order:
        table[dimension] = pd.Categorical(table[dimension], categories=order, ordered=True)
        table = table.sort_values(dimension)
    fig = px.bar(table, x="dropout", y=dimension, orientation="h", text=table["dropout"].round(1).astype(str) + "%", title=title, color_discrete_sequence=["#b94a48"], hover_data={"students": True, "dropout": ":.2f"})
    fig.update_traces(textposition="outside")
    fig.update_xaxes(title="Observed dropout rate (%)", range=[0, max(100, table["dropout"].max() * 1.18 if not table.empty else 100)])
    return _base(fig, max(300, 38 * len(table) + 80))


def outcome_matrix(df: pd.DataFrame, dimension: str, title: str) -> go.Figure:
    table = df.groupby([dimension, "Target"]).size().unstack(fill_value=0).reindex(columns=OUTCOMES, fill_value=0)
    pct = table.div(table.sum(axis=1), axis=0).mul(100).round(1)
    fig = px.imshow(pct, text_auto=True, aspect="auto", color_continuous_scale=["#f5f7f4", "#2f7d68"], labels=dict(x="Outcome", y=dimension, color="Percent"), title=title)
    return _base(fig, max(320, 34 * len(pct) + 80))


def risk_distribution(df: pd.DataFrame, column: str, title: str) -> go.Figure:
    order = ["LOW", "MEDIUM", "HIGH"]
    counts = df[column].value_counts().reindex(order, fill_value=0).rename_axis("Risk").reset_index(name="Students")
    fig = px.bar(counts, x="Risk", y="Students", color="Risk", category_orders={"Risk": order}, color_discrete_map={"LOW":"#2f7d68", "MEDIUM":"#c58a31", "HIGH":"#b94a48"}, text="Students", title=title)
    return _base(fig, 300)


def academic_outcome_box(df: pd.DataFrame, metric: str, title: str) -> go.Figure:
    fig = px.box(df, x="Target", y=metric, color="Target", category_orders={"Target": OUTCOMES}, color_discrete_map=OUTCOME_COLORS, points=False, title=title)
    return _base(fig)
