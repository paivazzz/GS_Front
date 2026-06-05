"""Feature: Visão Geral (panorama nacional).

Abre a narrativa de dados (storytelling): primeiro os KPIs do país, depois a
evolução temporal e, por fim, onde se concentram os focos (ranking + bioma).
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from ..pipelines import fire_pipeline
from ..ui import charts, components


def renderizar(focos: pd.DataFrame) -> None:
    """Renderiza a aba de visão geral a partir dos focos já filtrados."""
    components.cabecalho(
        "Panorama nacional de queimadas",
        "Visão consolidada dos focos de calor detectados por satélite no período selecionado.",
    )

    # KPIs — reutiliza o componente cartao_metrica via linha_metricas.
    k = fire_pipeline.kpis(focos)
    components.linha_metricas(
        [
            {"rotulo": "Focos detectados", "valor": f"{k['total_focos']:,}".replace(",", ".")},
            {"rotulo": "FRP médio", "valor": f"{k['frp_medio']:.0f} MW", "delta": "potência radiativa"},
            {"rotulo": "FRP máximo", "valor": f"{k['frp_max']:.0f} MW", "delta": "foco mais intenso",
             "cor": charts.theme.COR_ACENTO},
            {"rotulo": "Estados ativos", "valor": f"{k['estados_ativos']}", "delta": "com focos no período"},
        ]
    )
    st.write("")

    # Evolução temporal (Plotly interativo).
    components.cabecalho("Evolução diária dos focos")
    serie = fire_pipeline.serie_diaria(focos)
    st.plotly_chart(charts.serie_temporal_focos(serie), width='stretch')

    # Concentração: ranking de estados + composição por bioma.
    col_esq, col_dir = st.columns([3, 2])
    with col_esq:
        components.cabecalho("Estados com mais focos")
        ranking = fire_pipeline.ranking_estados(focos).head(8)
        st.plotly_chart(
            charts.grafico_barras(ranking, x="estado", y="focos", horizontal=True),
            width='stretch',
        )
    with col_dir:
        components.cabecalho("Distribuição por bioma")
        por_bioma = fire_pipeline.resumo_por_bioma(focos)
        st.plotly_chart(charts.pizza_bioma(por_bioma), width='stretch')
