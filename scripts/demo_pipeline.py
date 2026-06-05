"""Demonstração das camadas de dados SEM a interface (prova de independência da UI).

Roda providers -> pipelines -> modelo de IA e imprime os resultados no console.
Mostra que a arquitetura não depende do Streamlit para funcionar — basta rodar:

    python -m scripts.demo_pipeline

Útil para depurar a lógica de negócio dentro do VS Code sem subir o app inteiro.
"""
from __future__ import annotations

from src.pipelines import climate_pipeline, fire_pipeline, risk_pipeline
from src.providers import climate_provider, satellite_provider


def main() -> None:
    print("=" * 70)
    print("SENTINELA Orbital — demo de pipeline (sem interface)")
    print("=" * 70)

    # 1) Providers
    focos = satellite_provider.gerar_focos(dias=90)
    clima = climate_provider.gerar_clima(dias=90)
    print(f"\n[providers] focos gerados: {len(focos):,}  |  registros de clima: {len(clima):,}")

    # 2) Pipelines de agregação
    kpis = fire_pipeline.kpis(focos)
    print(f"[pipeline] KPIs: {kpis}")
    print("\n[pipeline] Top 5 estados por focos:")
    print(fire_pipeline.ranking_estados(focos).head(5).to_string(index=False))

    # 3) Modelo de IA
    modelo, metricas = risk_pipeline.treinar_modelo()
    print(f"\n[modelo] acurácia de validação: {metricas['acuracia']*100:.1f}%")
    print(f"[modelo] importância das features: {metricas['importancias']}")

    snapshot = climate_pipeline.snapshot_por_estado(clima)
    feat = risk_pipeline.construir_features(focos, snapshot)
    pred = risk_pipeline.prever_risco(modelo, feat)
    print("\n[modelo] risco previsto por estado:")
    print(
        pred[["estado", "risco_label", "risco_prob", "focos_total", "focos_dia", "dias_sem_chuva"]]
        .to_string(index=False)
    )
    print("\nOK — todas as camadas executaram sem o Streamlit.")


if __name__ == "__main__":
    main()
