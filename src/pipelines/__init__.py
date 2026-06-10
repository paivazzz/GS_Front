"""Camada de Pipelines: orquestração e transformação de dados.

Recebe os DataFrames brutos dos providers e produz visões limpas, agregadas e
enriquecidas (séries temporais, rankings, tabela de features de risco). Não depende
de Streamlit e pode ser executada e testada isoladamente (ver scripts/demo_pipeline.py).
"""
