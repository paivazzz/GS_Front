"""Geo provider: catálogo estático de estados, regiões e biomas brasileiros.

Fornece centroides (lat/lon) usados para posicionar os focos de calor no mapa e
para os filtros geográficos. Dados estáticos e curados (não dependem de RNG).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Estado:
    """Representa uma Unidade Federativa monitorada e seus metadados geográficos."""

    uf: str
    nome: str
    regiao: str
    bioma: str
    lat: float
    lon: float


# Recorte com os estados mais relevantes para monitoramento de queimadas
# (Amazônia, Cerrado e Pantanal concentram a maior parte dos focos no Brasil).
_ESTADOS: list[Estado] = [
    Estado("AM", "Amazonas", "Norte", "Amazônia", -3.42, -65.86),
    Estado("PA", "Pará", "Norte", "Amazônia", -3.79, -52.48),
    Estado("RO", "Rondônia", "Norte", "Amazônia", -10.83, -63.34),
    Estado("AC", "Acre", "Norte", "Amazônia", -9.02, -70.81),
    Estado("TO", "Tocantins", "Norte", "Cerrado", -10.17, -48.30),
    Estado("MA", "Maranhão", "Nordeste", "Cerrado", -5.42, -45.44),
    Estado("BA", "Bahia", "Nordeste", "Caatinga", -12.58, -41.70),
    Estado("MT", "Mato Grosso", "Centro-Oeste", "Cerrado", -12.64, -55.42),
    Estado("MS", "Mato Grosso do Sul", "Centro-Oeste", "Pantanal", -20.51, -54.54),
    Estado("GO", "Goiás", "Centro-Oeste", "Cerrado", -15.93, -50.14),
    Estado("MG", "Minas Gerais", "Sudeste", "Cerrado", -18.10, -44.38),
    Estado("SP", "São Paulo", "Sudeste", "Mata Atlântica", -22.19, -48.79),
]


def listar_estados() -> list[Estado]:
    """Retorna a lista completa de estados monitorados."""
    return list(_ESTADOS)


def mapa_por_uf() -> dict[str, Estado]:
    """Indexa os estados por sigla (UF) para lookup rápido."""
    return {e.uf: e for e in _ESTADOS}


def listar_biomas() -> list[str]:
    """Retorna os biomas distintos, em ordem alfabética."""
    return sorted({e.bioma for e in _ESTADOS})


def listar_regioes() -> list[str]:
    """Retorna as regiões distintas, em ordem alfabética."""
    return sorted({e.regiao for e in _ESTADOS})
