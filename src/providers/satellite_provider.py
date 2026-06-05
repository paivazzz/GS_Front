"""Satellite provider: focos de calor (queimadas) simulados no padrão NASA FIRMS / INPE.

Cada linha representa um foco de calor detectado por satélite, com os mesmos campos
que uma API real exporia: localização, brilho (temperatura de brilho em Kelvin),
FRP (Fire Radiative Power, em MW), confiança da detecção e satélite de origem.

A geração é determinística (seed) para garantir reprodutibilidade. A intensidade de
focos por estado é modulada pelo bioma (Amazônia/Cerrado/Pantanal queimam mais) e
por uma sazonalidade que cresce em direção à estação seca.
"""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from .geo_provider import listar_estados

# Data de referência "hoje" do sistema (mantém o dataset estável entre execuções).
DATA_REFERENCIA = date(2026, 6, 2)

# Peso relativo de queimadas por bioma (Pantanal e Cerrado são os mais críticos).
_PESO_BIOMA = {
    "Amazônia": 1.0,
    "Cerrado": 1.2,
    "Pantanal": 1.6,
    "Caatinga": 0.6,
    "Mata Atlântica": 0.4,
}

_SATELITES = ["AQUA_M-T", "TERRA_M-M", "NOAA-20", "SUOMI-NPP", "GOES-16"]


def _sazonalidade(dia_offset: int, total_dias: int) -> float:
    """Fator sazonal: cresce conforme avança para a estação seca (fim da janela).

    Retorna um multiplicador entre ~0.5 e ~1.8 usando uma curva suave.
    """
    progresso = dia_offset / max(total_dias - 1, 1)
    return 0.5 + 1.3 * (progresso**1.5)


def gerar_focos(dias: int = 90, seed: int = 42) -> pd.DataFrame:
    """Gera um DataFrame de focos de calor para os últimos ``dias``.

    Args:
        dias: tamanho da janela temporal terminando em ``DATA_REFERENCIA``.
        seed: semente do gerador aleatório (reprodutibilidade).

    Returns:
        DataFrame com uma linha por foco detectado.
    """
    rng = np.random.default_rng(seed)
    estados = listar_estados()
    registros: list[dict] = []

    for offset in range(dias):
        dia = DATA_REFERENCIA - timedelta(days=dias - 1 - offset)
        fator_sazonal = _sazonalidade(offset, dias)

        for est in estados:
            peso = _PESO_BIOMA.get(est.bioma, 0.7)
            # Número esperado de focos no dia para o estado.
            lam = max(0.1, 6.0 * peso * fator_sazonal)
            n_focos = int(rng.poisson(lam))
            if n_focos == 0:
                continue

            # Dispersa os focos em torno do centroide do estado.
            lats = est.lat + rng.normal(0, 1.4, n_focos)
            lons = est.lon + rng.normal(0, 1.4, n_focos)
            # FRP segue cauda longa (poucos focos muito intensos).
            frp = rng.gamma(shape=2.0, scale=18.0 * peso, size=n_focos).round(1)
            brilho = (305 + rng.gamma(2.0, 6.0, n_focos)).round(1)
            confianca = rng.integers(45, 100, n_focos)

            for i in range(n_focos):
                registros.append(
                    {
                        "data": pd.Timestamp(dia),
                        "uf": est.uf,
                        "estado": est.nome,
                        "regiao": est.regiao,
                        "bioma": est.bioma,
                        "lat": round(float(lats[i]), 4),
                        "lon": round(float(lons[i]), 4),
                        "frp_mw": float(frp[i]),
                        "brilho_k": float(brilho[i]),
                        "confianca": int(confianca[i]),
                        "satelite": _SATELITES[rng.integers(0, len(_SATELITES))],
                    }
                )

    df = pd.DataFrame.from_records(registros)
    df.insert(0, "foco_id", range(1, len(df) + 1))
    return df
