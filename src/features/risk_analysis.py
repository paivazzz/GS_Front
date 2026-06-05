"""Feature: Análise de Risco com IA + Feedback Humano (human-in-the-loop).

Esta é a tela que cumpre o requisito de "Feedback Humano": o modelo de IA classifica
o risco de queimada por estado e SUGERE alertas de evacuação para os estados em risco
Alto/Crítico. O envio do alerta NÃO é automático — um operador da Defesa Civil precisa
APROVAR ou DESCARTAR cada sugestão, e a decisão fica registrada no estado da sessão.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from ..pipelines import risk_pipeline
from ..state import session
from ..ui import charts, components


def _painel_features_modelo(metricas: dict) -> None:
    """Mostra a importância das features do modelo (reusa grafico_barras)."""
    imp = (
        pd.DataFrame(
            {"feature": list(metricas["importancias"].keys()),
             "importancia": list(metricas["importancias"].values())}
        )
        .sort_values("importancia")
    )
    st.plotly_chart(
        charts.grafico_barras(imp, x="feature", y="importancia",
                              cor="#3CA0FF", horizontal=True),
        width='stretch',
    )


def _fluxo_human_in_the_loop(criticos: pd.DataFrame) -> None:
    """Renderiza os cards de aprovação/descarte de alertas de evacuação."""
    components.cabecalho(
        "Triagem de alertas (human-in-the-loop)",
        "O modelo sugere alertas para estados em risco Alto/Crítico. Um operador deve "
        "revisar e decidir — nenhum alerta é disparado automaticamente.",
    )

    if criticos.empty:
        st.success("✅ Nenhum estado em risco Alto ou Crítico no período filtrado.")
        return

    for _, linha in criticos.iterrows():
        uf = linha["uf"]
        decisao = session.decisao_de(uf)
        with st.container(border=True):
            col_info, col_acao = st.columns([3, 2])
            with col_info:
                st.markdown(
                    f"**{linha['estado']} ({uf})** &nbsp; {components.badge_risco(linha['risco_label'])}",
                    unsafe_allow_html=True,
                )
                st.caption(
                    f"Confiança do modelo: {linha['risco_prob']:.0f}% · "
                    f"{int(linha['focos_total'])} focos · {linha['dias_sem_chuva']} dias sem chuva · "
                    f"umidade {linha['umidade']:.0f}%"
                )
            with col_acao:
                if decisao:
                    icone = "📤" if decisao["decisao"] == "Aprovado" else "🚫"
                    st.markdown(
                        f"{icone} **{decisao['decisao']}** em {decisao['quando']}"
                    )
                else:
                    b1, b2 = st.columns(2)
                    if b1.button("📤 Aprovar alerta", key=f"aprovar_{uf}", width='stretch'):
                        session.registrar_decisao(uf, "Aprovado", linha["risco_label"])
                        st.rerun()
                    if b2.button("🚫 Descartar", key=f"descartar_{uf}", width='stretch'):
                        session.registrar_decisao(uf, "Descartado", linha["risco_label"])
                        st.rerun()


def renderizar(focos: pd.DataFrame, clima_snapshot: pd.DataFrame, modelo, metricas: dict) -> None:
    """Renderiza a aba de análise de risco completa."""
    components.cabecalho(
        "Classificação de risco por IA",
        "Modelo RandomForest cruza atividade de focos (satélite) com variáveis "
        "climáticas para estimar o risco de queimada de cada estado.",
    )

    with st.spinner("Executando inferência do modelo de risco…"):
        features = risk_pipeline.construir_features(focos, clima_snapshot)
        resultado = risk_pipeline.prever_risco(modelo, features)

    if resultado.empty:
        st.info("Sem dados suficientes para inferência. Ajuste os filtros.")
        return

    # KPIs de risco — reutiliza cartao_metrica com cores semânticas.
    contagem = resultado["risco_label"].value_counts()
    components.linha_metricas(
        [
            {"rotulo": "Risco Crítico", "valor": str(contagem.get("Crítico", 0)),
             "delta": "estados", "cor": charts.theme.COR_RISCO["Crítico"]},
            {"rotulo": "Risco Alto", "valor": str(contagem.get("Alto", 0)),
             "delta": "estados", "cor": charts.theme.COR_RISCO["Alto"]},
            {"rotulo": "Risco Moderado", "valor": str(contagem.get("Moderado", 0)),
             "delta": "estados", "cor": charts.theme.COR_RISCO["Moderado"]},
            {"rotulo": "Risco Baixo", "valor": str(contagem.get("Baixo", 0)),
             "delta": "estados", "cor": charts.theme.COR_RISCO["Baixo"]},
        ]
    )
    st.write("")

    col_esq, col_dir = st.columns([3, 2])
    with col_esq:
        components.cabecalho("Ranking de risco por estado")
        tabela = resultado[
            ["estado", "bioma", "risco_label", "risco_prob", "focos_total", "temp_max", "umidade", "dias_sem_chuva"]
        ].rename(
            columns={
                "estado": "Estado", "bioma": "Bioma", "risco_label": "Risco",
                "risco_prob": "Confiança (%)", "focos_total": "Focos", "temp_max": "Temp. máx (°C)",
                "umidade": "Umidade (%)", "dias_sem_chuva": "Dias s/ chuva",
            }
        )
        st.dataframe(tabela, width='stretch', hide_index=True)
    with col_dir:
        components.cabecalho("Seca x risco")
        st.pyplot(charts.dispersao_clima_risco(resultado), width='stretch')

    st.divider()
    criticos = resultado[resultado["risco_classe"] >= 2].reset_index(drop=True)
    _fluxo_human_in_the_loop(criticos)

    if st.session_state.get("alertas_decididos"):
        if st.button("↺ Reiniciar triagem"):
            session.resetar_decisoes()
            st.rerun()

    st.divider()
    with st.expander("🤖 Como o modelo decide (importância das variáveis)"):
        st.caption(
            f"Acurácia de validação: **{metricas['acuracia']*100:.1f}%** · "
            f"{metricas['n_treino']} amostras de treino · {metricas['n_validacao']} de validação."
        )
        _painel_features_modelo(metricas)
