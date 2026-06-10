"""Testes do pipeline de focos: provam que a camada roda sem o Streamlit.

Executar: python -m pytest -q   (ou)   python -m pytest tests/test_fire_pipeline.py -v
"""
import pandas as pd

from src.pipelines import fire_pipeline
from src.providers import satellite_provider


def _focos():
    return satellite_provider.gerar_focos(dias=30, seed=1)


def test_geracao_deterministica():
    """Mesma seed -> mesmo dataset (reprodutibilidade)."""
    a = satellite_provider.gerar_focos(dias=10, seed=99)
    b = satellite_provider.gerar_focos(dias=10, seed=99)
    pd.testing.assert_frame_equal(a, b)


def test_colunas_esperadas():
    df = _focos()
    for col in ["foco_id", "data", "uf", "bioma", "lat", "lon", "frp_mw", "confianca"]:
        assert col in df.columns


def test_filtro_confianca():
    df = _focos()
    filtrado = fire_pipeline.aplicar_filtros(
        df, df["data"].min(), df["data"].max(), biomas=None, confianca_min=80
    )
    assert (filtrado["confianca"] >= 80).all()


def test_filtro_intervalo_de_datas():
    df = _focos()
    inicio = df["data"].min() + pd.Timedelta(days=5)
    fim = df["data"].max() - pd.Timedelta(days=5)
    filtrado = fire_pipeline.aplicar_filtros(df, inicio, fim, None, 0)
    assert filtrado["data"].min() >= inicio
    assert filtrado["data"].max() <= fim


def test_serie_diaria_soma_consistente():
    df = _focos()
    serie = fire_pipeline.serie_diaria(df)
    assert serie["focos"].sum() == len(df)


def test_kpis_em_df_vazio():
    vazio = _focos().iloc[0:0]
    k = fire_pipeline.kpis(vazio)
    assert k["total_focos"] == 0 and k["estados_ativos"] == 0
