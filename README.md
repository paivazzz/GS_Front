# SENTINELA Orbital

Dashboard de monitoramento de queimadas e risco climático via satélite.
Global Solution 2026/1 - FIAP - Front-End & Mobile Development em Sistemas de IA.

Consome dados de satélite, clima e geolocalização, classifica o risco de queimada por
estado com IA e sugere alertas de evacuação — que um operador humano aprova ou descarta.

## 1. O problema

Secas e queimadas destroem lavouras, ecossistemas e vidas. Satélites da NASA FIRMS e do
INPE detectam milhares de focos por dia, mas o dado cru não ajuda quem está na ponta
(Defesa Civil, produtor rural) se não virar uma tela clara e rápida.

## 2. A solução

Dashboard em Streamlit com quatro telas:

- **Visão Geral**: KPIs nacionais, evolução diária dos focos, ranking de estados e
  distribuição por bioma.
- **Mapa de Focos**: mapa interativo georreferenciado, colorido pela potência radiativa
  (FRP), com tabela dos focos mais intensos.
- **Análise de Risco (IA)**: um RandomForest classifica o risco de cada estado (Baixo a
  Crítico) e abre o fluxo de aprovação de alertas com revisão humana.
- **Clima**: tendências de temperatura, umidade, precipitação e dias sem chuva por estado.

## 3. De onde vêm os dados

Os dados são simulados de forma determinística (seed fixa): a aplicação roda offline e
sempre gera o mesmo resultado. A simulação segue o formato de uma API real, então trocar
por dados de verdade é simples — basta mexer na camada `providers/` (trocar a geração
sintética por chamadas HTTP e manter as colunas de saída). Nenhuma outra camada muda.

- **Focos** (`providers/satellite_provider.py`): padrão NASA FIRMS / INPE — `lat`, `lon`,
  `frp_mw`, `brilho_k`, `confianca`, `satelite`, `data`.
- **Clima** (`providers/climate_provider.py`): séries diárias por estado (temperatura,
  umidade, precipitação, vento, dias sem chuva), formato ERA5 / INMET / OpenWeather.

## 4. Arquitetura

Código em camadas, sem arquivo monolítico. O `app.py` só monta a tela.

- `src/providers/`: acesso aos dados brutos. Em produção, é onde entrariam as chamadas HTTP.
- `src/pipelines/`: transformação, agregação e modelo de risco. Não depende do Streamlit.
- `src/features/`: uma tela por arquivo.
- `src/state/`: controle do `st.session_state`, incluindo a fila de decisões de alerta.
- `src/ui/`: design system, componentes reutilizáveis, sidebar e gráficos.

## 5. Requisitos da disciplina no código

- **Estado e ciclo de execução**: `state/session.py` e cache em `data_loader.py`.
- **`@st.cache_data` / `@st.cache_resource`**: `data_loader.py` (dados e modelo treinado
  uma vez só).
- **Arquitetura em camadas**: `src/{providers,pipelines,features,state,ui}/`.
- **3+ filtros interativos**: datas, biomas e confiança na sidebar, mais seleção de estados
  na aba Clima.
- **2+ gráficos (1+ Plotly interativo)**: Plotly na série temporal, mapa, barras e pizza;
  Matplotlib na dispersão seca x risco.
- **Componente reutilizável**: `ui/components.cartao_metrica` e `ui/charts.grafico_barras`.
- **Layout (tabs/colunas/sidebar)**: `app.py` e `st.columns` nas features.
- **Latência**: `st.spinner` nas features e `time.sleep` simulando a rede.
- **Cores semânticas**: `ui/theme.COR_RISCO` (verde a vermelho) em KPIs, badges e gráficos.
- **Human-in-the-loop**: `features/risk_analysis.py`, onde se aprova ou descarta cada alerta.

## 6. Como executar

Requer Python 3.10+.

```bash
python -m venv .venv                 # opcional, mas recomendado
.venv\Scripts\Activate.ps1           # Windows (PowerShell)
source .venv/bin/activate            # Linux/Mac

pip install -r requirements.txt
streamlit run app.py                 # abre em http://localhost:8501
```

> **Windows:** se der `streamlit não é reconhecido`, a pasta de scripts não está no PATH.
> Use `python -m streamlit run app.py`.

Sem interface: `python -m scripts.demo_pipeline` · Testes: `python -m pytest -q`

## 7. Deploy público

- **Streamlit Community Cloud**: conecte o repositório em [share.streamlit.io](https://share.streamlit.io)
  e aponte para `app.py`.
- **Hugging Face Spaces**: crie um Space do tipo Streamlit e suba os arquivos; o `app.py`
  na raiz já é o ponto de entrada.

---

Projeto acadêmico da Global Solution FIAP 2026/1. Os dados de focos e clima são simulados
para demonstração e o sistema "SENTINELA Orbital" é fictício.
