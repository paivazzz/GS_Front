"""Climate provider: séries meteorológicas diárias simuladas por estado.

Reproduz o tipo de dado que viria de uma API climática (ex.: OpenWeather, INMET,
reanálise ERA5 derivada de satélite): temperatura máxima, umidade relativa,
precipitação, velocidade do vento e dias consecutivos sem chuva.

Estes campos alimentam o índice de risco de queimada (pipeline de risco).
"""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from .geo_provider import listar_estados
from .satellite_provider import DATA_REFERENCIA

# Perfis climáticos base por bioma (temp média, umidade média, prob. de chuva diária).
_PERFIL_BIOMA = {
    "Amazônia": {"temp": 32.0, "umid": 78.0, "p_chuva": 0.45},
    "Cerrado": {"temp": 34.0, "umid": 45.0, "p_chuva": 0.18},
    "Pantanal": {"temp": 35.0, "umid": 40.0, "p_chuva": 0.12},
    "Caatinga": {"temp": 36.0, "umid": 35.0, "p_chuva": 0.08},
    "Mata Atlântica": {"temp": 28.0, "umid": 70.0, "p_chuva": 0.40},
}


def gerar_clima(dias: int = 90, seed: int = 7) -> pd.DataFrame:
    """Gera séries climáticas diárias por estado para os últimos ``dias``.

    Returns:
        DataFrame com uma linha por (estado, dia).
    """
    rng = np.random.default_rng(seed)
    estados = listar_estados()
    registros: list[dict] = []

    for est in estados:
        perfil = _PERFIL_BIOMA.get(est.bioma, {"temp": 30.0, "umid": 55.0, "p_chuva": 0.25})
        dias_sem_chuva = 0

        for offset in range(dias):
            dia = DATA_REFERENCIA - timedelta(days=dias - 1 - offset)
            # Tendência de seca: probabilidade de chuva cai ao longo da janela.
            progresso = offset / max(dias - 1, 1)
            p_chuva = max(0.03, perfil["p_chuva"] * (1.0 - 0.6 * progresso))
            choveu = rng.random() < p_chuva
            precip = float(rng.gamma(2.0, 6.0)) if choveu else 0.0

            if choveu and precip > 1.0:
                dias_sem_chuva = 0
            else:
                dias_sem_chuva += 1

            temp_max = perfil["temp"] + 4.0 * progresso + rng.normal(0, 1.8)
            umidade = perfil["umid"] - 12.0 * progresso + rng.normal(0, 4.0)
            umidade = float(np.clip(umidade, 8.0, 100.0))

            registros.append(
                {
                    "data": pd.Timestamp(dia),
                    "uf": est.uf,
                    "estado": est.nome,
                    "regiao": est.regiao,
                    "bioma": est.bioma,
                    "temp_max": round(float(temp_max), 1),
                    "umidade": round(umidade, 1),
                    "precip_mm": round(precip, 1),
                    "vento_kmh": round(float(np.clip(rng.normal(14, 5), 0, 60)), 1),
                    "dias_sem_chuva": int(dias_sem_chuva),
                }
            )

    return pd.DataFrame.from_records(registros)
