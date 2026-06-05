"""Componentes de UI reutilizáveis.

`cartao_metrica` é o componente reutilizável exigido pela disciplina: ele é
invocado em múltiplos lugares (visão geral e análise de risco) com parâmetros
diferentes. Os demais (badge, cabeçalho) também são reaproveitados entre telas.
"""
from __future__ import annotations

import streamlit as st

from . import theme


def cabecalho(titulo: str, subtitulo: str = "") -> None:
    """Renderiza um cabeçalho de seção padronizado (reutilizado em todas as telas)."""
    st.markdown(f"### {titulo}")
    if subtitulo:
        st.markdown(f"<div class='so-sub'>{subtitulo}</div>", unsafe_allow_html=True)
    st.write("")


def cartao_metrica(rotulo: str, valor: str, delta: str = "", cor: str | None = None) -> None:
    """Cartão de KPI reutilizável.

    Args:
        rotulo: nome do indicador (ex.: "Focos detectados").
        valor: valor formatado já como string (ex.: "1.204").
        delta: texto auxiliar abaixo do valor (ex.: "+12% vs. ontem").
        cor: cor opcional do valor (usada para dar leitura semântica ao número).
    """
    estilo_valor = f"color:{cor};" if cor else ""
    st.markdown(
        f"""
        <div class="so-card">
            <div class="rotulo">{rotulo}</div>
            <div class="valor" style="{estilo_valor}">{valor}</div>
            <div class="delta">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge_risco(label: str) -> str:
    """Retorna o HTML de um badge colorido conforme o nível de risco (semântico)."""
    cor = theme.COR_RISCO.get(label, theme.COR_TEXTO_SUAVE)
    return f"<span class='so-badge' style='background:{cor}'>{label}</span>"


def linha_metricas(itens: list[dict]) -> None:
    """Compõe uma linha de cartões de métrica a partir de uma lista de specs.

    Cada item: {"rotulo":..., "valor":..., "delta":..., "cor":...}. Demonstra o
    reuso de ``cartao_metrica`` em diferentes contextos/parametrizações.
    """
    colunas = st.columns(len(itens))
    for coluna, item in zip(colunas, itens):
        with coluna:
            cartao_metrica(
                item["rotulo"], item["valor"], item.get("delta", ""), item.get("cor")
            )
