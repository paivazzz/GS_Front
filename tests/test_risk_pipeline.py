"""Testes do pipeline de risco (modelo de IA), independentes do Streamlit."""
from src.pipelines import climate_pipeline, risk_pipeline
from src.providers import climate_provider, satellite_provider


def test_modelo_treina_e_tem_acuracia_razoavel():
    """O modelo deve treinar e atingir acurácia bem acima do acaso (4 classes => 25%)."""
    _, metricas = risk_pipeline.treinar_modelo()
    assert metricas["acuracia"] > 0.6
    assert set(metricas["importancias"].keys()) == set(risk_pipeline.FEATURES)


def test_construir_features_uma_linha_por_estado():
    focos = satellite_provider.gerar_focos(dias=20, seed=3)
    clima = climate_provider.gerar_clima(dias=20, seed=3)
    snapshot = climate_pipeline.snapshot_por_estado(clima)
    feat = risk_pipeline.construir_features(focos, snapshot)
    assert feat["uf"].is_unique
    for col in risk_pipeline.FEATURES:
        assert col in feat.columns
    assert feat["focos_total"].notna().all()
    assert feat["focos_dia"].notna().all()


def test_predicao_anexa_rotulos_validos():
    modelo, _ = risk_pipeline.treinar_modelo()
    focos = satellite_provider.gerar_focos(dias=20, seed=5)
    clima = climate_provider.gerar_clima(dias=20, seed=5)
    snapshot = climate_pipeline.snapshot_por_estado(clima)
    feat = risk_pipeline.construir_features(focos, snapshot)
    pred = risk_pipeline.prever_risco(modelo, feat)
    assert set(pred["risco_label"]).issubset(set(risk_pipeline.RISCO_LABELS.values()))
    assert pred["risco_prob"].between(0, 100).all()
