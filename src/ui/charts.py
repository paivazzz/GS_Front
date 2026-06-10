"""Funções de visualização reutilizáveis (Plotly interativo + Matplotlib).

O `grafico_barras` é genérico de propósito e aparece em vários lugares (ranking de
estados, composição por bioma, importância das features do modelo).

Plotly cuida das visualizações principais, com hover e zoom. O Matplotlib entra só
no gráfico complementar de clima x risco.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from . import theme

# Layout base aplicado a todos os gráficos Plotly (identidade visual consistente).
_LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=theme.COR_TEXTO),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def mapa_focos(df: pd.DataFrame) -> go.Figure:
    """Mapa interativo de focos de calor, colorido pela intensidade (FRP).

    Usa OpenStreetMap, então não precisa de token do Mapbox. Tons mais quentes são
    focos mais intensos.
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(**_LAYOUT_BASE, title="Sem focos para os filtros selecionados")
        return fig

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="frp_mw",
        size="frp_mw",
        size_max=18,
        color_continuous_scale="Inferno",
        hover_name="estado",
        hover_data={"bioma": True, "frp_mw": ":.1f", "confianca": True, "lat": False, "lon": False},
        zoom=3.0,
        center={"lat": -13.5, "lon": -52.0},
    )
    fig.update_layout(
        **_LAYOUT_BASE,
        mapbox_style="open-street-map",
        coloraxis_colorbar=dict(title="FRP (MW)"),
        height=520,
    )
    return fig


def serie_temporal_focos(serie: pd.DataFrame) -> go.Figure:
    """Linha temporal interativa: nº de focos por dia + FRP total (eixo secundário)."""
    fig = go.Figure()
    if not serie.empty:
        fig.add_trace(
            go.Scatter(
                x=serie["data"], y=serie["focos"], name="Focos/dia",
                mode="lines", line=dict(color=theme.COR_ACENTO, width=2.5),
                fill="tozeroy", fillcolor="rgba(255,90,60,0.15)",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=serie["data"], y=serie["frp_total"], name="FRP total (MW)",
                mode="lines", line=dict(color="#3CA0FF", width=1.8, dash="dot"), yaxis="y2",
            )
        )
    fig.update_layout(
        **_LAYOUT_BASE,
        height=340,
        yaxis=dict(title="Focos", gridcolor=theme.COR_BORDA),
        yaxis2=dict(title="FRP (MW)", overlaying="y", side="right", showgrid=False),
        xaxis=dict(gridcolor=theme.COR_BORDA),
    )
    return fig


def grafico_barras(
    df: pd.DataFrame, x: str, y: str, titulo: str = "", cor: str | None = None, horizontal: bool = False
) -> go.Figure:
    """Gráfico de barras genérico.

    Serve ao ranking de estados, à composição por bioma e à importância das features
    do modelo. Cada chamada passa colunas e orientação diferentes.
    """
    orient = "h" if horizontal else "v"
    fig = px.bar(
        df, x=y if horizontal else x, y=x if horizontal else y,
        orientation=orient, title=titulo,
        color_discrete_sequence=[cor or theme.COR_ACENTO],
    )
    fig.update_layout(**_LAYOUT_BASE, height=340, xaxis=dict(gridcolor=theme.COR_BORDA),
                      yaxis=dict(gridcolor=theme.COR_BORDA))
    return fig


def pizza_bioma(df: pd.DataFrame) -> go.Figure:
    """Rosca (donut) da distribuição de focos por bioma."""
    fig = px.pie(
        df, names="bioma", values="focos", hole=0.55,
        color_discrete_sequence=theme.SEQUENCIA_PLOTLY,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(**_LAYOUT_BASE, height=340, showlegend=False)
    return fig


def dispersao_clima_risco(df: pd.DataFrame):
    """Gráfico em Matplotlib: umidade x dias sem chuva, colorido por risco.

    Mostra a relação entre seca e o risco previsto. Retorna uma Figure do Matplotlib,
    renderizada via st.pyplot.
    """
    fig, ax = plt.subplots(figsize=(6, 3.4))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    if not df.empty:
        for label, cor in theme.COR_RISCO.items():
            sub = df[df["risco_label"] == label]
            if not sub.empty:
                ax.scatter(sub["dias_sem_chuva"], sub["umidade"], s=80, c=cor,
                           label=label, edgecolors="white", linewidths=0.5, alpha=0.9)
    ax.set_xlabel("Dias sem chuva", color=theme.COR_TEXTO)
    ax.set_ylabel("Umidade (%)", color=theme.COR_TEXTO)
    ax.tick_params(colors=theme.COR_TEXTO_SUAVE)
    for spine in ax.spines.values():
        spine.set_color(theme.COR_BORDA)
    leg = ax.legend(title="Risco", fontsize=8, labelcolor=theme.COR_TEXTO, framealpha=0)
    leg.get_title().set_color(theme.COR_TEXTO)
    fig.tight_layout()
    return fig
