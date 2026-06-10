"""Sidebar de filtros: desenha os controles e devolve o estado deles.

Mostra o logotipo, os filtros (datas, bioma, confiança) e o status do modelo de IA.
Retorna um ``Filtros`` que as features consomem, então a sidebar é a única fonte de
verdade dos filtros globais.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import pandas as pd
import streamlit as st

from ..providers import geo_provider
from . import theme


@dataclass
class Filtros:
    """Estado consolidado dos filtros globais selecionados pelo usuário."""

    data_inicio: date
    data_fim: date
    biomas: list[str] = field(default_factory=list)
    confianca_min: int = 50


def renderizar(data_min: date, data_max: date, metricas_modelo: dict | None = None) -> Filtros:
    """Desenha a sidebar e retorna os filtros escolhidos.

    Args:
        data_min/data_max: limites do período disponível no dataset.
        metricas_modelo: métricas do modelo de IA para exibir no rodapé (opcional).
    """
    with st.sidebar:
        st.markdown(theme.logo(), unsafe_allow_html=True)
        st.divider()

        st.markdown("#### Filtros")
        # Intervalo de datas.
        periodo = st.date_input(
            "Período de análise",
            value=(data_max - pd.Timedelta(days=30), data_max),
            min_value=data_min,
            max_value=data_max,
            format="DD/MM/YYYY",
        )
        if isinstance(periodo, tuple) and len(periodo) == 2:
            data_inicio, data_fim = periodo
        else:  # usuário ainda escolhendo a 2ª data
            data_inicio = data_fim = periodo if isinstance(periodo, date) else data_max

        # Biomas (múltipla escolha).
        biomas = st.multiselect(
            "Biomas",
            options=geo_provider.listar_biomas(),
            default=geo_provider.listar_biomas(),
            help="Filtra os focos pelos biomas selecionados.",
        )

        # Confiança mínima da detecção.
        confianca_min = st.slider(
            "Confiança mínima da detecção (%)",
            min_value=0, max_value=100, value=50, step=5,
            help="Descarta focos detectados com baixa confiança pelo satélite.",
        )

        st.divider()
        if metricas_modelo:
            st.markdown("#### Modelo de risco")
            st.caption(
                f"RandomForest · acurácia de validação **{metricas_modelo['acuracia']*100:.1f}%** "
                f"({metricas_modelo['n_treino']} amostras de treino)."
            )
        st.caption(f"Última atualização: {st.session_state.get('ultima_atualizacao', '-')}")

    return Filtros(
        data_inicio=data_inicio,
        data_fim=data_fim,
        biomas=biomas,
        confianca_min=confianca_min,
    )
