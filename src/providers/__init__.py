"""Camada de Providers: acesso a dados externos / brutos.

Em produção, estes módulos fariam chamadas HTTP a APIs reais (ex.: NASA FIRMS,
INPE Queimadas, OpenWeather). Aqui geramos dados simulados de forma determinística
(seed fixa) para que o dashboard seja 100% reproduzível offline, mantendo o mesmo
contrato de saída (DataFrames) que um provider real exporia.
"""
