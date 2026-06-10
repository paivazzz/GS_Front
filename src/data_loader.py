"""Carregamento dos dados e do modelo, com o cache do Streamlit.

É o único lugar que chama os providers e o treino do modelo, escolhendo o tipo de
cache certo para cada caso:

* ``@st.cache_data`` para DataFrames (focos, clima): só recomputam se os argumentos
  mudarem.
* ``@st.cache_resource`` para o modelo treinado, que é compartilhado entre sessões e
  reusado a cada rerun sem retreinar.

Sem isso, cada mudança de filtro regeraria todos os dados e retreinaria o modelo,
deixando o app lento à toa.
"""
from __future__ import annotations

import time

import pandas as pd
import streamlit as st

from .pipelines import risk_pipeline
from .providers import climate_provider, satellite_provider


@st.cache_data(show_spinner=False)
def carregar_focos(dias: int = 90) -> pd.DataFrame:
    """Carrega (e cacheia) os focos de calor dos últimos ``dias``."""
    time.sleep(0.6)  # simula a latência de uma chamada de rede
    return satellite_provider.gerar_focos(dias=dias)


@st.cache_data(show_spinner=False)
def carregar_clima(dias: int = 90) -> pd.DataFrame:
    """Carrega (e cacheia) as séries climáticas dos últimos ``dias``."""
    time.sleep(0.4)
    return climate_provider.gerar_clima(dias=dias)


@st.cache_resource(show_spinner=False)
def carregar_modelo() -> tuple:
    """Treina (uma única vez) e cacheia o modelo de risco e suas métricas."""
    return risk_pipeline.treinar_modelo()
