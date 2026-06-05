"""Pipeline climático: agregação de séries meteorológicas por estado.

Consolida as séries diárias em uma "foto" recente por estado (médias da janela e
último valor de dias sem chuva), usada tanto nos gráficos de clima quanto como
insumo para a tabela de features do modelo de risco.
"""
from __future__ import annotations

import pandas as pd


def serie_climatica(df: pd.DataFrame, ufs: list[str] | None = None) -> pd.DataFrame:
    """Filtra a série climática por estados selecionados (todos se ``None``)."""
    if ufs:
        return df[df["uf"].isin(ufs)].reset_index(drop=True)
    return df.reset_index(drop=True)


def media_diaria_nacional(df: pd.DataFrame) -> pd.DataFrame:
    """Média diária nacional de temperatura e umidade (visão de tendência)."""
    if df.empty:
        return pd.DataFrame(columns=["data", "temp_max", "umidade", "precip_mm"])
    return (
        df.groupby("data")
        .agg(temp_max=("temp_max", "mean"), umidade=("umidade", "mean"), precip_mm=("precip_mm", "sum"))
        .round(1)
        .reset_index()
        .sort_values("data")
    )


def snapshot_por_estado(df: pd.DataFrame) -> pd.DataFrame:
    """Consolida a janela em uma linha por estado (médias + último dia sem chuva).

    É o insumo climático cruzado com os focos para montar as features de risco.
    """
    if df.empty:
        return pd.DataFrame(
            columns=["uf", "estado", "bioma", "temp_max", "umidade", "precip_mm", "dias_sem_chuva"]
        )
    ultimo_dia = df.sort_values("data").groupby("uf").tail(1)[["uf", "dias_sem_chuva"]]
    agg = (
        df.groupby(["uf", "estado", "bioma"])
        .agg(temp_max=("temp_max", "mean"), umidade=("umidade", "mean"), precip_mm=("precip_mm", "mean"))
        .round(1)
        .reset_index()
    )
    return agg.merge(ultimo_dia, on="uf", how="left")
