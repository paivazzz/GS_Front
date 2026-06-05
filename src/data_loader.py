"""Orquestração de carregamento com cache do Streamlit.

Concentra o ponto onde os providers (custosos) e o treino do modelo de IA são
chamados, aplicando a estratégia de cache correta:

* ``@st.cache_data``  -> para DataFrames (focos, clima): serializáveis e imutáveis
  entre reruns; só recomputam se os argumentos mudarem.
* ``@st.cache_resource`` -> para o modelo treinado (objeto não-serializável que deve
  ser compartilhado entre sessões e reusado a cada rerun, sem retreinar).

Sem este cache, cada interação do usuário (mudar um filtro) re-geraria todos os
dados e re-treinaria o modelo, tornando o app lento — exatamente o que a disciplina
pede para evitar.
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
    time.sleep(0.6)  # simula latência de uma chamada de rede real (design p/ latência)
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
