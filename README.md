# 🛰️ SENTINELA Orbital

**Dashboard de monitoramento de queimadas e risco climático via satélite**
Global Solution 2026/1 · FIAP · Disciplina **Front-End & Mobile Development em Sistemas de IA**

> Plataforma que transforma volumes massivos de dados de satélite, climáticos e
> geolocalizados em **informação acionável** para a Defesa Civil e o agronegócio —
> com classificação de risco por IA e um fluxo de decisão humano-no-loop para
> disparo de alertas de evacuação.

---

## 1. O problema (impacto espacial)

Eventos climáticos extremos — secas prolongadas e queimadas — destroem lavouras,
ecossistemas e vidas. Satélites como os da rede **NASA FIRMS** e do **Programa
Queimadas do INPE** detectam milhares de focos de calor por dia, mas esse volume
bruto é inútil para quem decide na ponta (um agente da Defesa Civil, um produtor
rural) se não for traduzido em uma interface clara, rápida e confiável.

O **SENTINELA Orbital** conecta a **exploração/observação espacial** a um desafio
real da sociedade brasileira: ele consome focos de calor detectados por satélite,
cruza com variáveis climáticas e **prioriza onde agir**, sugerindo alertas que um
operador humano revisa antes de disparar.

## 2. A solução

Um dashboard interativo em **Streamlit** organizado em 4 telas:

| Aba | O que entrega |
|-----|---------------|
| 📊 **Visão Geral** | KPIs nacionais, evolução diária de focos, ranking de estados e distribuição por bioma (storytelling: do panorama ao detalhe). |
| 🗺️ **Mapa de Focos** | Mapa interativo georreferenciado (hover + zoom) colorido pela potência radiativa (FRP) + tabela dos focos mais intensos. |
| 🔥 **Análise de Risco (IA)** | Modelo RandomForest classifica o risco por estado (Baixo→Crítico) e abre o **fluxo human-in-the-loop** de aprovação de alertas de evacuação. |
| 🌡️ **Clima** | Tendências de temperatura, umidade, precipitação e dias sem chuva por estado. |

## 3. Fonte de dados

Os dados são **simulados de forma determinística** (seed fixa) para que a POC rode
100% offline e reproduzível, **mas respeitando o contrato de uma API real**:

- **Focos de calor** (`providers/satellite_provider.py`): mesmos campos do padrão
  **NASA FIRMS / INPE** — `lat`, `lon`, `frp_mw` (Fire Radiative Power),
  `brilho_k` (brightness temperature), `confianca`, `satelite`, `data`.
- **Clima** (`providers/climate_provider.py`): séries diárias por estado
  (temperatura máx., umidade, precipitação, vento, dias sem chuva), no formato de
  uma reanálise tipo **ERA5 / INMET / OpenWeather**.

> **Trocar por dados reais** exige alterar apenas a camada `providers/`: basta
> substituir a geração sintética por chamadas HTTP às APIs, mantendo as colunas de
> saída. Nenhuma outra camada muda — é o ganho da arquitetura desacoplada.

## 4. Por que Streamlit (e não Gradio)?

- O caso é um **dashboard analítico multi-tela** com filtros globais, layout em
  colunas/abas/sidebar e muitos gráficos — terreno onde o modelo declarativo do
  Streamlit (`st.tabs`, `st.columns`, `st.sidebar`) é mais direto que o paradigma
  event-driven do Gradio.
- O controle de **rerun + cache** (`@st.cache_data` / `@st.cache_resource`) modela
  perfeitamente o requisito de evitar recomputar dados/modelo a cada interação.
- **Deploy gratuito** trivial em Streamlit Community Cloud e Hugging Face Spaces.

## 5. Arquitetura

Código **componentizado em camadas** (nada de arquivo monolítico):

```
┌──────────────────────────────────────────────────────────────┐
│                          app.py                                │
│   composição: page config · tema · cache · filtros · abas      │
└───────────────┬───────────────────────────────┬──────────────┘
                │                                 │
        ┌───────▼────────┐               ┌────────▼────────┐
        │   features/    │  usa a UI ──► │       ui/        │
        │ overview       │               │ theme (design    │
        │ fire_map       │               │ system) · charts │
        │ risk_analysis  │               │ components ·     │
        │ climate_trends │               │ sidebar          │
        └───────┬────────┘               └─────────────────┘
                │ consome
        ┌───────▼────────┐     ┌──────────────┐     ┌──────────┐
        │   pipelines/   │◄────│   state/     │     │ providers/│
        │ fire_pipeline  │     │ session      │     │ satellite │
        │ climate_pipe   │     │ (session_    │     │ climate   │
        │ risk_pipeline  │     │  state)      │     │ geo       │
        │ (modelo de IA) │     └──────────────┘     └────┬─────┘
        └───────┬────────┘                               │
                └───────────── dados ◄───────────────────┘
```

| Camada | Pasta | Responsabilidade |
|--------|-------|------------------|
| **Providers** | `src/providers/` | Acesso a dados externos / brutos (focos, clima, geo). Em produção, chamadas HTTP. |
| **Pipelines** | `src/pipelines/` | Transformação, agregação e o **modelo de IA** de risco. Independente do Streamlit. |
| **Features** | `src/features/` | Cada aba/tela com uma responsabilidade. |
| **State** | `src/state/` | Gerenciamento centralizado de `st.session_state` (inclui a fila de decisões de alerta). |
| **UI** | `src/ui/` | Design system, componentes reutilizáveis, sidebar e gráficos. |

## 6. Mapeamento dos requisitos da disciplina → onde está no código

| Requisito | Implementação |
|-----------|---------------|
| Ciclo de execução + estado | `st.session_state` em `state/session.py`; cache em `data_loader.py` |
| `@st.cache_data` / `@st.cache_resource` | `data_loader.py` (dados cacheados; modelo treinado uma vez) |
| Arquitetura em camadas (não-monolítica) | `src/{providers,pipelines,features,state,ui}/` |
| ≥ 3 filtros interativos | datas + biomas + confiança (sidebar) **+** estados (aba Clima) |
| ≥ 2 gráficos (mín. 1 Plotly interativo) | Plotly: série temporal, mapa, barras, pizza · Matplotlib: dispersão seca×risco |
| Componente reutilizável | `ui/components.cartao_metrica` e `ui/charts.grafico_barras` usados em várias telas |
| Layout (tabs/colunas/sidebar) | `app.py` (tabs + sidebar) e `st.columns` nas features |
| Design para latência | `st.spinner` nas features + `time.sleep` simulando rede em `data_loader.py` |
| Cores semânticas | `ui/theme.COR_RISCO` (verde→vermelho) aplicado em KPIs, badges e gráficos |
| **Feedback humano (human-in-the-loop)** | `features/risk_analysis.py`: aprovar/descartar alerta de evacuação sugerido pela IA |

## 7. Diferenciais implementados

- 🤖 **Modelo de IA treinado** (RandomForest, scikit-learn) classificando risco em 4 níveis.
- 🎨 **Design system próprio**: nome, logo, paleta e CSS consistentes (`ui/theme.py`).
- 🔗 **Múltiplas fontes cruzadas**: focos de satélite + clima alimentam o modelo.
- ✅ **Testes automatizados** (`tests/`) e **script de pipeline sem UI** (`scripts/demo_pipeline.py`).
- 📖 **Storytelling de dados**: do panorama nacional ao foco individual no mapa.

## 8. Como executar

Requer **Python 3.10+**.

```bash
# 1. clonar e entrar no projeto
git clone <url-do-repositorio>
cd <pasta-do-repositorio>

# 2. (recomendado) criar um ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. instalar dependências
pip install -r requirements.txt

# 4. rodar o dashboard
streamlit run app.py
```

A aplicação abre em `http://localhost:8501`.

### Rodar a lógica sem a interface (prova de independência da UI)

```bash
python -m scripts.demo_pipeline
```

### Rodar os testes

```bash
python -m pytest -q
```

## 9. Deploy público

**Streamlit Community Cloud:** conecte o repositório em
[share.streamlit.io](https://share.streamlit.io), aponte para `app.py` e publique.

**Hugging Face Spaces:** crie um Space do tipo *Streamlit*, suba os arquivos
(o `app.py` na raiz já é o ponto de entrada) e o Space instala o `requirements.txt`
automaticamente.

## 10. Estrutura de pastas

```
.
├── app.py                      # ponto de entrada (composição)
├── requirements.txt
├── README.md
├── .streamlit/config.toml      # tema nativo do Streamlit
├── src/
│   ├── data_loader.py          # carregamento com cache (@st.cache_data/resource)
│   ├── providers/              # satellite · climate · geo
│   ├── pipelines/              # fire · climate · risk (modelo de IA)
│   ├── features/               # overview · fire_map · risk_analysis · climate_trends
│   ├── state/                  # session (gerência de st.session_state)
│   └── ui/                     # theme · components · sidebar · charts
├── scripts/
│   └── demo_pipeline.py        # roda as camadas sem o Streamlit
└── tests/                      # testes de pipeline e do modelo
```

## 11. Vídeo

> 🎥 _Link do vídeo (YouTube não listado) a ser inserido aqui._

---

_Projeto acadêmico desenvolvido para a Global Solution FIAP 2026/1. Dados de focos
e clima são simulados para fins de demonstração; o sistema "SENTINELA Orbital" é
fictício._
