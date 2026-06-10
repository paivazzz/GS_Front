"""Feature: Mapa de Focos.

Mostra os focos georreferenciados em um mapa interativo (com hover e zoom) e uma
tabela com os focos mais intensos do período.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from ..ui import charts, components


def renderizar(focos: pd.DataFrame) -> None:
    """Renderiza o mapa e a tabela de focos a partir dos dados filtrados."""
    components.cabecalho(
        "Mapa de focos de calor",
        "Cada ponto é um foco detectado por satélite; tamanho e cor representam a "
        "potência radiativa (FRP). Use o scroll para dar zoom e passe o mouse para detalhes.",
    )

    with st.spinner("Renderizando focos..."):
        st.plotly_chart(charts.mapa_focos(focos), width='stretch')

    components.cabecalho("Focos mais intensos no período")
    if focos.empty:
        st.info("Nenhum foco corresponde aos filtros atuais.")
        return

    tabela = (
        focos.sort_values("frp_mw", ascending=False)
        .head(15)[["data", "estado", "bioma", "frp_mw", "brilho_k", "confianca", "satelite"]]
        .rename(
            columns={
                "data": "Data", "estado": "Estado", "bioma": "Bioma",
                "frp_mw": "FRP (MW)", "brilho_k": "Brilho (K)",
                "confianca": "Confiança (%)", "satelite": "Satélite",
            }
        )
    )
    tabela["Data"] = pd.to_datetime(tabela["Data"]).dt.strftime("%d/%m/%Y")
    st.dataframe(tabela, width='stretch', hide_index=True)
