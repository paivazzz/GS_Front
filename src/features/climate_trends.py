"""Feature: Tendências Climáticas.

Mostra a evolução de temperatura, umidade e precipitação — variáveis que explicam
o aumento do risco de queimada — com filtro próprio por estado.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..pipelines import climate_pipeline
from ..providers import geo_provider
from ..ui import charts, components


def _grafico_temp_umidade(serie: pd.DataFrame) -> go.Figure:
    """Linha dupla interativa: temperatura (eixo esq.) e umidade (eixo dir.)."""
    fig = go.Figure()
    if not serie.empty:
        fig.add_trace(go.Scatter(x=serie["data"], y=serie["temp_max"], name="Temp. máx (°C)",
                                 line=dict(color="#E8730C", width=2.5)))
        fig.add_trace(go.Scatter(x=serie["data"], y=serie["umidade"], name="Umidade (%)",
                                 line=dict(color="#3CA0FF", width=2.5), yaxis="y2"))
    fig.update_layout(
        **charts._LAYOUT_BASE, height=360,
        yaxis=dict(title="Temp. máx (°C)", gridcolor=charts.theme.COR_BORDA),
        yaxis2=dict(title="Umidade (%)", overlaying="y", side="right", showgrid=False),
        xaxis=dict(gridcolor=charts.theme.COR_BORDA),
    )
    return fig


def renderizar(clima: pd.DataFrame) -> None:
    """Renderiza a aba de tendências climáticas."""
    components.cabecalho(
        "Tendências climáticas",
        "Calor e baixa umidade prolongados antecedem os picos de queimada. "
        "Acompanhe a janela seca por estado.",
    )

    # Filtro local extra (além dos globais da sidebar): seleção de estados.
    ufs = st.multiselect(
        "Estados",
        options=[e.uf for e in geo_provider.listar_estados()],
        default=["MT", "MS", "PA"],
        help="Compare a evolução climática de estados específicos.",
    )

    serie_estados = climate_pipeline.serie_climatica(clima, ufs)
    nacional = climate_pipeline.media_diaria_nacional(serie_estados)

    components.cabecalho("Temperatura x umidade (média dos estados selecionados)")
    st.plotly_chart(_grafico_temp_umidade(nacional), width='stretch')

    col_esq, col_dir = st.columns(2)
    with col_esq:
        components.cabecalho("Precipitação acumulada por dia")
        st.plotly_chart(
            charts.grafico_barras(nacional, x="data", y="precip_mm", cor="#3CA0FF"),
            width='stretch',
        )
    with col_dir:
        components.cabecalho("Dias sem chuva (situação atual)")
        snapshot = climate_pipeline.snapshot_por_estado(serie_estados).sort_values(
            "dias_sem_chuva", ascending=False
        )
        st.plotly_chart(
            charts.grafico_barras(snapshot, x="estado", y="dias_sem_chuva",
                                  cor=charts.theme.COR_ACENTO, horizontal=True),
            width='stretch',
        )
