"""SENTINELA Orbital — ponto de entrada da aplicação Streamlit.

Responsabilidade: compor a aplicação. Configura a página, aplica o design system,
carrega os dados (com cache), inicializa o estado, renderiza a sidebar de filtros e
distribui o fluxo para as features (abas). Toda a lógica vive nas camadas em ``src/``.

Execução:  streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from src.data_loader import carregar_clima, carregar_focos, carregar_modelo
from src.features import climate_trends, fire_map, overview, risk_analysis
from src.pipelines import climate_pipeline, fire_pipeline
from src.providers.satellite_provider import DATA_REFERENCIA
from src.state import session
from src.ui import sidebar, theme

st.set_page_config(
    page_title="SENTINELA Orbital",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    theme.aplicar_tema()
    session.inicializar()

    # --- Carregamento com cache (dados custosos + modelo treinado) ---
    with st.spinner("Conectando aos satélites e carregando dados…"):
        focos_raw = carregar_focos()
        clima_raw = carregar_clima()
        modelo, metricas_modelo = carregar_modelo()

    data_min = focos_raw["data"].min().date()
    data_max = focos_raw["data"].max().date()

    # --- Sidebar (filtros globais reutilizáveis) ---
    filtros = sidebar.renderizar(data_min, data_max, metricas_modelo)

    # --- Aplicação dos filtros (pipeline) ---
    focos = fire_pipeline.aplicar_filtros(
        focos_raw, filtros.data_inicio, filtros.data_fim, filtros.biomas, filtros.confianca_min
    )
    clima_filtrado = clima_raw[
        (clima_raw["data"] >= str(filtros.data_inicio)) & (clima_raw["data"] <= str(filtros.data_fim))
    ]
    if filtros.biomas:
        clima_filtrado = clima_filtrado[clima_filtrado["bioma"].isin(filtros.biomas)]
    clima_snapshot = climate_pipeline.snapshot_por_estado(clima_filtrado)

    # --- Cabeçalho principal ---
    col_logo, col_status = st.columns([3, 1])
    with col_logo:
        st.markdown(theme.logo(), unsafe_allow_html=True)
    with col_status:
        st.markdown(
            f"<div style='text-align:right;color:{theme.COR_TEXTO_SUAVE};font-size:0.8rem'>"
            f"Referência: {DATA_REFERENCIA.strftime('%d/%m/%Y')}<br>"
            f"{len(focos):,} focos no recorte atual</div>".replace(",", "."),
            unsafe_allow_html=True,
        )
    st.divider()

    # --- Abas (features) ---
    aba_geral, aba_mapa, aba_risco, aba_clima = st.tabs(
        ["📊 Visão Geral", "🗺️ Mapa de Focos", "🔥 Análise de Risco (IA)", "🌡️ Clima"]
    )
    with aba_geral:
        overview.renderizar(focos)
    with aba_mapa:
        fire_map.renderizar(focos)
    with aba_risco:
        risk_analysis.renderizar(focos, clima_snapshot, modelo, metricas_modelo)
    with aba_clima:
        climate_trends.renderizar(clima_filtrado)


if __name__ == "__main__":
    main()
