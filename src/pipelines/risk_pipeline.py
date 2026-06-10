"""Pipeline de risco: o modelo de IA que classifica o risco de queimada por estado.

Treinamos um RandomForest (scikit-learn) para classificar cada estado em quatro
níveis (Baixo, Moderado, Alto e Crítico) a partir de variáveis climáticas e da
atividade de focos detectada por satélite.

Como não temos um dataset rotulado embutido, geramos uma amostra sintética de treino
a partir de uma função latente (uma regra física plausível) com ruído e treinamos o
modelo sobre ela. Depois aplicamos esse modelo às features reais agregadas dos
providers. A acurácia de validação aparece na interface, para não esconder nada.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Ordem das features, igual no treino e na predição.
# Usamos ``focos_dia`` (média diária por estado) em vez do total da janela para o
# modelo não depender do tamanho do período que o usuário filtrou.
FEATURES = ["temp_max", "umidade", "precip_mm", "dias_sem_chuva", "focos_dia", "frp_medio"]

RISCO_LABELS = {0: "Baixo", 1: "Moderado", 2: "Alto", 3: "Crítico"}
RISCO_CORES = {"Baixo": "#2E9E5B", "Moderado": "#E5B700", "Alto": "#E8730C", "Crítico": "#D63230"}


def _score_latente(X: pd.DataFrame) -> np.ndarray:
    """Função latente que traduz as features em um escore contínuo de risco.

    Quanto mais quente, seco, com mais dias sem chuva e mais focos intensos,
    maior o escore. Chuva reduz o risco.
    """
    return (
        0.040 * X["temp_max"]
        + 0.025 * (100 - X["umidade"])
        + 0.050 * X["dias_sem_chuva"]
        - 0.050 * X["precip_mm"]
        + 0.040 * X["focos_dia"]
        + 0.005 * X["frp_medio"]
    )


def _rotular(score: np.ndarray) -> np.ndarray:
    """Quebra o escore contínuo em 4 classes de risco por limiares fixos.

    Os limiares ficam perto dos quartis da amostra de treino, para as classes saírem
    equilibradas e o classificador aprender melhor.
    """
    return np.select(
        [score < 3.2, score < 4.6, score < 6.0],
        [0, 1, 2],
        default=3,
    )


def _gerar_dados_treino(n: int = 4000, seed: int = 42) -> tuple[pd.DataFrame, np.ndarray]:
    """Gera amostra sintética de treino cobrindo o espaço de features plausível."""
    rng = np.random.default_rng(seed)
    X = pd.DataFrame(
        {
            "temp_max": rng.uniform(20, 45, n),
            "umidade": rng.uniform(8, 100, n),
            "precip_mm": rng.gamma(1.5, 4.0, n),
            "dias_sem_chuva": rng.integers(0, 60, n),
            "focos_dia": rng.uniform(0, 40, n),
            "frp_medio": rng.gamma(2.0, 20.0, n),
        }
    )
    score = _score_latente(X) + rng.normal(0, 0.25, n)  # o ruído evita um problema trivial demais
    y = _rotular(score)
    return X, y


def treinar_modelo(seed: int = 42) -> tuple[RandomForestClassifier, dict]:
    """Treina o classificador de risco e retorna (modelo, métricas de validação)."""
    X, y = _gerar_dados_treino(seed=seed)
    X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    modelo = RandomForestClassifier(n_estimators=120, max_depth=10, random_state=seed, n_jobs=-1)
    modelo.fit(X_tr, y_tr)
    acc = accuracy_score(y_val, modelo.predict(X_val))
    metricas = {
        "acuracia": round(float(acc), 3),
        "n_treino": int(len(X_tr)),
        "n_validacao": int(len(X_val)),
        "importancias": dict(zip(FEATURES, modelo.feature_importances_.round(3))),
    }
    return modelo, metricas


def construir_features(focos_df: pd.DataFrame, clima_snapshot: pd.DataFrame) -> pd.DataFrame:
    """Cruza atividade de focos (por estado) com o snapshot climático.

    Returns:
        Uma linha por estado com todas as colunas de ``FEATURES`` preenchidas.
    """
    if clima_snapshot.empty:
        return pd.DataFrame(columns=["uf", "estado", "bioma", "focos_total", *FEATURES])

    if focos_df.empty:
        focos_agg = pd.DataFrame(columns=["uf", "focos_total", "frp_medio"])
        dias = 1
    else:
        focos_agg = (
            focos_df.groupby("uf")
            .agg(focos_total=("foco_id", "count"), frp_medio=("frp_mw", "mean"))
            .reset_index()
        )
        # Número de dias distintos na janela, para normalizar focos por dia.
        dias = max(1, focos_df["data"].dt.normalize().nunique())

    feat = clima_snapshot.merge(focos_agg, on="uf", how="left")
    feat["focos_total"] = feat["focos_total"].fillna(0).astype(int)
    feat["frp_medio"] = feat["frp_medio"].fillna(0.0).round(1)
    feat["focos_dia"] = (feat["focos_total"] / dias).round(2)
    return feat


def prever_risco(modelo: RandomForestClassifier, features: pd.DataFrame) -> pd.DataFrame:
    """Aplica o modelo às features e anexa classe, rótulo e probabilidade de risco.

    A coluna ``risco_prob`` é a probabilidade da classe prevista (a confiança do
    modelo), que ajuda o operador a priorizar o que revisar primeiro.
    """
    if features.empty:
        return features.assign(risco_classe=[], risco_label=[], risco_prob=[])

    X = features[FEATURES]
    classes = modelo.predict(X)
    probs = modelo.predict_proba(X).max(axis=1)
    out = features.copy()
    out["risco_classe"] = classes.astype(int)
    out["risco_label"] = [RISCO_LABELS[c] for c in classes]
    out["risco_prob"] = (probs * 100).round(1)
    return out.sort_values("risco_classe", ascending=False).reset_index(drop=True)
