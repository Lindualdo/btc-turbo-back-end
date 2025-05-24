# BTC Turbo

## 🎯 Objetivo do Negócio

Desenvolver um sistema inteligente para maximizar lucros e mitigar riscos em operações de Hold Alavancado de Bitcoin (BTC) na Plataforma AAVE da rede Arbitrum. O projeto visa integrar análises de força de tendência, riscos técnicos, financeiros, estruturais, macroeconômicos e de plataforma para fornecer orientações estratégicas e auxiliar usuários em suas decisões de investimento.

## 📌 Última versão: v1.0.19 - Analise de ciclos
-- Revisão no BTC X EMA 200
-- Refatoração na função principal para usar a pontuação de cada indicador (limpeza no codigo)
-- Refattoração para mostrar Score X ponderação de cada indicador
-- Organização e documentação do codigo
-- Refatorado a função principal analyze_btc_cycles_v2(tv), logica completa em cada indicador, ela apenas consolida
-- Api será usada como modelo para as demais implementações
-- #PENDENCIA DE REFATORAR# Retirar funções não utilizadas e criar Utils para cada indicador
-- Corrigiu a escala 0-10 (era limitada a 9.0)
-- Eliminou o erro JSON com validações de segurança
-- Padronizou campo "detalhes" em todos indicadores
-- Adicionou resumo executivo com estratégias
-- Removeu nomenclatura V2 desnecessária
-- Implementou fallbacks inteligentes
-- Refatoração compketa no indicador BTC X Realized Price - Agora usando dados reais 12 meses

## 🏗️ Arquitetura do Projeto (Pastas e Arquivos)

```
/
├── .DS_Store
├── .env.example
├── .gitattributes
├── .gitignore
├── Dockerfile
├── README.md
├── requirements.txt
└── app
    ├── __init__.py
    ├── config.py
    ├── dependencies.py
    ├── main.py
    ├── models
    │   └── __init__.py
    ├── routers
    │   ├── __init__.py
    │   ├── analise_ciclos.py
    │   ├── analise_fundamentos.py
    │   ├── analise_tecnica_emas.py
    │   └── analise_riscos.py
    ├── services
    │   ├── __init__.py
    │   ├── btc_analysis.py
    │   ├── fundamentals.py
    │   ├── tv_session_manager.py
    │   └── risk_analysis.py
    ├── utils
    │   ├── __init__.py
    │   └── ema_utils.py
    ├── docs
    │   ├── analise_ciclos.md
    │   ├── analise_fundamentos.md
    │   ├── analise_riscos.md
    │   └── analise_tecnica_emas.md
```

## 🌏 Infraestrutura & Deploy

### 🚀 Railway (Produção)
- Ambiente provisionado com Docker + FastAPI.
- Deploy contínuo via GitHub (branch `main`).
- Variáveis de ambiente configuradas manualmente:
  - `TV_USERNAME`
  - `TV_PASSWORD`
  - `NOTION_TOKEN`
  - `NOTION_DATABASE_ID_EMA`
  - `NOTION_DATABASE_ID_MACRO`
  - `WALLET_ADDRESS`

---

## 🚀 Dependências Principais

- `FastAPI` / `Uvicorn`
- `tvDatafeed` (via GitHub: `rongarDF`)
- `pandas`
- `notion-client`
- `pydantic-settings >= 2.0.0`
- `web3`

---

## 🔧 Padrões Técnicos

- APIs organizadas por domínio (`/v1/analise-tecnica-emas`, `/v1/analise-ciclos`).
- Separação clara entre lógica, serviços e configuração.
- `config.py` centralizado via `BaseSettings` e `@lru_cache`.
- Dockerfile controlado manualmente (Railway via modo Dockerfile).
- Swagger e OpenAPI prontos para uso.
- Uso de query parameters para `username` e `password` (TV).
- 📚 Cada novo endpoint deve seguir o padrão `routers + services + utils`.

```python
app.include_router(analise_tecnica_emas.router, prefix="/api/v1")
```

### Nos Routers usar assim
```python
@router.get("/analise-ciclos", 
            summary="Análise de ciclos do BTC", 
            tags=["Ciclos"])
```

---

## 📝 APIs do Sistema

### 🗓️ Medir a Força da Tendência

- `v1/analise-tecnica-emas - feito`
- `v1/analise-ciclos - feito`
- `v1/analise-fundamentos - feito`
- `v1/forca-tendencia (consolida a pontuação final) - a fazer`

### 🗓️ Medir os Riscos Técnicos

- `/v1/analise-tecnica-rsi (sobrecompra) - feito`
- `/v1/analise-divergencia-rsi - feito`
- `v1/analise-tendencia-risco (emas) - feito`
- `v1/risco-tecnico (consolidar pontuação) - a fazer`

### 🗓️ Medir os Riscos Financeiros

- `/v1/risco-financeiro (HF e Alavancagem) - feito`

### 🗓️ Medir os Riscos Estruturais

- `v1/riscos-estruturais (Model Variance, MVRV, VDD, Fear & Greed) - a fazer` 

### 🗓️ Medir os Riscos Macroeconômicos

- `v1/riscos-macro (MOVE, DXY, VIX, US10Y, Ouro, M2 Global) - a fazer` 

### 🗓️ Medir os Riscos de Plataforma

- `v1/riscos-plataforma (AAVE, Arbitrum, Ethereum, WBTC) - a fazer` 

### 🗓️ Consolidar Todos os Riscos e Gerar Indicador Final

- `v1/analise-riscos - a fazer/revisar`

---

## Refactore

- Refatorar API análise risco financeiro para deixar apenas web3 para busca dos dados.
- Refatorar funções de leitura do Notion para padronizar o Database ID.
- Excluir variáveis de ambiente não usadas.
- Refatorar arquivo btc_analisys.py decompor em funções menores (utils), está ficando muito grande e cpmplexo para manutenção