"""Design system do SENTINELA Orbital: paleta semântica, tipografia e CSS.

Centraliza a identidade visual (cores, fontes, espaçamentos) para garantir
consistência entre telas — um dos diferenciais sugeridos ("design system próprio").
As cores de risco são SEMÂNTICAS: verde = seguro, amarelo/laranja = atenção,
vermelho = crítico.
"""
from __future__ import annotations

import streamlit as st

# Paleta da marca (tema "orbital" escuro).
COR_FUNDO = "#0B0E17"
COR_PAINEL = "#141A29"
COR_BORDA = "#243049"
COR_TEXTO = "#E8ECF4"
COR_TEXTO_SUAVE = "#8A93A6"
COR_ACENTO = "#FF5A3C"  # laranja-fogo da marca

# Cores semânticas de risco (consistentes com risk_pipeline.RISCO_CORES).
COR_RISCO = {
    "Baixo": "#2E9E5B",
    "Moderado": "#E5B700",
    "Alto": "#E8730C",
    "Crítico": "#D63230",
}

# Template de cores para gráficos Plotly (mesma família visual).
SEQUENCIA_PLOTLY = ["#FF5A3C", "#E5B700", "#3CA0FF", "#2E9E5B", "#B05CFF", "#FF8FA3"]


def aplicar_tema() -> None:
    """Injeta o CSS global do design system na página."""
    st.markdown(
        f"""
        <style>
            .stApp {{
                background: radial-gradient(1200px 600px at 80% -10%, #16203a 0%, {COR_FUNDO} 55%);
                color: {COR_TEXTO};
            }}
            section[data-testid="stSidebar"] {{
                background-color: {COR_PAINEL};
                border-right: 1px solid {COR_BORDA};
            }}
            h1, h2, h3, h4 {{ color: {COR_TEXTO}; font-weight: 700; }}
            /* Cartão reutilizável de métrica/insight */
            .so-card {{
                background: {COR_PAINEL};
                border: 1px solid {COR_BORDA};
                border-radius: 14px;
                padding: 18px 20px;
                box-shadow: 0 4px 18px rgba(0,0,0,0.25);
            }}
            .so-card .rotulo {{
                color: {COR_TEXTO_SUAVE};
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
            }}
            .so-card .valor {{ font-size: 1.9rem; font-weight: 800; line-height: 1.1; }}
            .so-card .delta {{ font-size: 0.85rem; color: {COR_TEXTO_SUAVE}; }}
            .so-badge {{
                display: inline-block; padding: 4px 12px; border-radius: 999px;
                font-weight: 700; font-size: 0.8rem; color: #0B0E17;
            }}
            .so-logo {{
                display: flex; align-items: center; gap: 12px; margin-bottom: 4px;
            }}
            .so-logo .mark {{
                font-size: 1.7rem; filter: drop-shadow(0 0 8px {COR_ACENTO});
            }}
            .so-logo .nome {{ font-size: 1.35rem; font-weight: 800; letter-spacing: 0.04em; }}
            .so-logo .nome span {{ color: {COR_ACENTO}; }}
            .so-sub {{ color: {COR_TEXTO_SUAVE}; font-size: 0.82rem; margin-top: -2px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def logo() -> str:
    """Retorna o HTML do logotipo do sistema fictício (usado na sidebar e no header)."""
    return (
        '<div class="so-logo">'
        '<span class="mark">🛰️</span>'
        '<div><div class="nome">SENTINELA<span> Orbital</span></div>'
        '<div class="so-sub">Monitoramento de queimadas via satélite</div></div>'
        "</div>"
    )
