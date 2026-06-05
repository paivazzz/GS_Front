"""Pipeline de focos de calor: limpeza, filtragem e agregação.

Funções puras (entram DataFrames, saem DataFrames) para serem facilmente testáveis
e reutilizáveis entre as features sem reprocessar os dados brutos.
"""
from __future__ import annotations

import pandas as pd


def aplicar_filtros(
    df: pd.DataFrame,
    data_inicio: pd.Timestamp,
    data_fim: pd.Timestamp,
    biomas: list[str] | None = None,
    confianca_min: int = 0,
) -> pd.DataFrame:
    """Filtra focos por intervalo de datas, biomas e confiança mínima.

    Args:
        df: DataFrame de focos brutos.
        data_inicio/data_fim: limites (inclusivos) do intervalo.
        biomas: lista de biomas a manter; ``None`` mantém todos.
        confianca_min: confiança mínima da detecção (0-100).
    """
    mask = (
        (df["data"] >= pd.Timestamp(data_inicio))
        & (df["data"] <= pd.Timestamp(data_fim))
        & (df["confianca"] >= confianca_min)
    )
    if biomas:
        mask &= df["bioma"].isin(biomas)
    return df.loc[mask].reset_index(drop=True)


def serie_diaria(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega focos por dia: contagem e FRP médio/total."""
    if df.empty:
        return pd.DataFrame(columns=["data", "focos", "frp_total", "frp_medio"])
    out = (
        df.groupby("data")
        .agg(focos=("foco_id", "count"), frp_total=("frp_mw", "sum"), frp_medio=("frp_mw", "mean"))
        .reset_index()
        .sort_values("data")
    )
    out["frp_total"] = out["frp_total"].round(1)
    out["frp_medio"] = out["frp_medio"].round(1)
    return out


def ranking_estados(df: pd.DataFrame) -> pd.DataFrame:
    """Ranqueia estados por número de focos (com FRP médio como métrica auxiliar)."""
    if df.empty:
        return pd.DataFrame(columns=["estado", "uf", "bioma", "focos", "frp_medio"])
    out = (
        df.groupby(["estado", "uf", "bioma"])
        .agg(focos=("foco_id", "count"), frp_medio=("frp_mw", "mean"))
        .reset_index()
        .sort_values("focos", ascending=False)
    )
    out["frp_medio"] = out["frp_medio"].round(1)
    return out.reset_index(drop=True)


def resumo_por_bioma(df: pd.DataFrame) -> pd.DataFrame:
    """Distribuição de focos por bioma (para gráfico de composição)."""
    if df.empty:
        return pd.DataFrame(columns=["bioma", "focos"])
    return (
        df.groupby("bioma")
        .agg(focos=("foco_id", "count"))
        .reset_index()
        .sort_values("focos", ascending=False)
        .reset_index(drop=True)
    )


def kpis(df: pd.DataFrame) -> dict[str, float]:
    """Calcula os indicadores-chave exibidos nos cartões do topo."""
    if df.empty:
        return {"total_focos": 0, "frp_medio": 0.0, "frp_max": 0.0, "estados_ativos": 0}
    return {
        "total_focos": int(len(df)),
        "frp_medio": round(float(df["frp_mw"].mean()), 1),
        "frp_max": round(float(df["frp_mw"].max()), 1),
        "estados_ativos": int(df["uf"].nunique()),
    }
