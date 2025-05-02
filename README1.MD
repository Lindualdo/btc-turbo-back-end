# 📄 Resumo Técnico do Projeto BTC Turbo

## 🎯 Objetivo
Criar uma API robusta e automatizada para **análise de ciclos do Bitcoin**, consolidando múltiplos indicadores técnicos, on-chain e macroeconômicos, com retorno estruturado para consumo por automações (n8n), dashboards ou bases de dados (ex: Notion).

---

## 🏗️ Arquitetura

- **Framework**: FastAPI  
- **Ambiente**: Railway (deploy contínuo)  
- **Organização modular**:
  - `btc_analysis.py`: funções de cálculo dos indicadores
  - `btc_cycles.py`: consolidação, lógica de pontuação e endpoint `/btc-cycles`
  - `requirements.txt`: bibliotecas de apoio
- **Exposição pública via endpoint GET `/btc-cycles`**
- **Autenticação**: via usuário/senha para TVDatafeed

---

## 📊 Indicadores implementados

| Indicador                     | Fonte               | Tipo           | Peso |
|------------------------------|---------------------|----------------|------|
| BTC vs 200D EMA              | TradingView         | Técnico        | 25%  |
| BTC vs Realized Price        | Valor fixo          | On-chain       | 25%  |
| Puell Multiple               | Notion API          | On-chain       | 20%  |
| BTC Dominance Tendência      | TradingView (BTC.D) | Técnico        | 20%  |
| Juros (US10Y - 90d)          | TradingView         | Macroeconômico | —    |
| Expansão Global              | Notion API          | Macroeconômico | —    |
| Macro Ambiente (consolidado)| Cálculo interno     | Macro final    | 10%  |

---

## 🧠 Lógica de pontuação

- Cada indicador retorna:
  - `pontuacao_bruta` (0, 1 ou 2)
  - `peso` e `pontuacao_ponderada`
- Consolidado final:
  - `score = soma(pontuacao_ponderada) → 0 a 2`
  - Escala convertida para 0 a 10
  - Classificação:
    - 🔴 Bear Forte (0–2)
    - 🟠 Bear Leve (2.1–4)
    - 🟡 Neutro (4.1–6)
    - 🔵 Bull Moderado (6.1–8)
    - 🟢 Bull Forte (8.1–10)

---

## 📦 Retorno do endpoint `/btc-cycles`

```json
{
  "dados_individuais": [...],
  "dados_consolidados": {
    "pontuacao_final": 7.6,
    "classificacao": "🔵 Bull Moderado",
    "estrategia": "Tamanho controlado",
    "data_processamento": "2025-05-02T20:10:00Z"
  },
  "resumo_executivo": [
    "🔹 BTC vs 200D EMA está forte",
    "⚠️ Puell Multiple está fraco",
    "ℹ️ BTC Dominance Tendência variou +2.3%"
  ]
}
```

---

## 🔌 Integrações

- 📥 Entrada via `tvDatafeed` com autenticação
- 📤 Exportação futura possível para:
  - Notion (registro histórico semanal)
  - Google Sheets (base de dados externa)
  - Frontend em painel via REST
