"""Estado da sessão do Streamlit, gerenciado em um lugar só.

Define os valores padrão, inicializa o ``st.session_state`` uma vez por sessão e
expõe helpers para registrar as decisões humanas sobre os alertas de evacuação.
As features não devem escrever no ``st.session_state`` direto: passam por aqui.
"""
from __future__ import annotations

from datetime import datetime

import streamlit as st

# Valores padrão das chaves de estado da aplicação.
_PADROES = {
    "alertas_decididos": {},  # {uf: {"decisao": str, "quando": str, "risco": str}}
    "tema_escuro": True,
    "ultima_atualizacao": None,
}


def inicializar() -> None:
    """Garante que todas as chaves de estado existam (idempotente)."""
    for chave, valor in _PADROES.items():
        if chave not in st.session_state:
            # Cópia para dicts mutáveis, evitando estado compartilhado entre sessões.
            st.session_state[chave] = dict(valor) if isinstance(valor, dict) else valor
    if st.session_state["ultima_atualizacao"] is None:
        st.session_state["ultima_atualizacao"] = datetime.now().strftime("%d/%m/%Y %H:%M")


def registrar_decisao(uf: str, decisao: str, risco: str) -> None:
    """Persiste no estado a decisão humana sobre um alerta de evacuação."""
    st.session_state["alertas_decididos"][uf] = {
        "decisao": decisao,
        "risco": risco,
        "quando": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }


def decisao_de(uf: str) -> dict | None:
    """Retorna a decisão já registrada para um estado, ou ``None``."""
    return st.session_state["alertas_decididos"].get(uf)


def resetar_decisoes() -> None:
    """Limpa todas as decisões registradas (botão 'reiniciar triagem')."""
    st.session_state["alertas_decididos"] = {}
