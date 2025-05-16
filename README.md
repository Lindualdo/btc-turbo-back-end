# 🚀 BTC Turbo API – v1.0.13

API em FastAPI para cálculo de indicadores técnicos e análise de ciclos do BTC, com deploy Dockerizado via Railway.

---

## 🛰️ Endpoints (Produção)

### 🚀 Ciclos BTC
```
GET /api/v1/analise-ciclos
```

### 🛈 EMAs BTC
```
GET /api/v1/analise-tecnica-emas
```

### 🛈 Fundamentos BTC
```
GET /api/v1/analise-fundamentos
```

### 🏥 Health Check
```
GET /health
```

### 🔧 Configurações Ativas
```
GET /config
```

### 🗃️ Swagger UI (Documentação)
```
GET /docs
```

### 🔎 OpenAPI JSON
```
GET /openapi.json
```

---

## 🏗️ Arquitetura do Projeto (pastas e arquivos)

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
    │   └── analise_tenica_emas.md
```

---

## 🌏 Infraestrutura & Deploy

### 🚀 Railway (produção)
- Ambiente provisionado com Docker + FastAPI
- Deploy contínuo via GitHub (branch `main`)
- Variáveis de ambiente configuradas manualmente:
  - `TV_USERNAME`
  - `TV_PASSWORD`
  - `NOTION_TOKEN`
  - `NOTION_DATABASE_ID_EMA`
  - `NOTION_DATABASE_ID_MACRO`

---

## 🚀 Dependências principais

- `FastAPI` / `Uvicorn`
- `tvDatafeed` (via GitHub: `rongarDF`)
- `pandas`
- `notion-client`
- `pydantic-settings >= 2.0.0`

---

## 🔧 Padrões Técnicos

- APIs organizadas por domínio (`/v1/analise-tecnica-emas`, `/v1/analise-ciclos`)
- Separação clara entre lógica, serviços e configuração
- `config.py` centralizado via `BaseSettings` e `@lru_cache`
- Dockerfile controlado manualmente (Railway via modo Dockerfile)
- Swagger e OpenAPI prontos para uso
- Uso de query parameters para `username` e `password` (TV)

---

# ⚙️ Diretrizes para próximos desenvolvimentos

- 📚 Cada novo endpoint deve seguir o padrão `routers + services + utils`

### Registro dos routers com prefixo versionado no main
```python
app.include_router(analise_tecnica_emas.router, prefix="/api/v1")
```

### Nos routers usar assim
```python
@router.get("/analise-ciclos", 
            summary="Análise de ciclos do BTC", 
            tags=["Ciclos"])
```

---

### 📝 APIs já concluídas e funcionando 100% estáveis

- `v1/analise-tecnica`
- `v1/analise-cliclos`
- `v1/analise-fundamentos`
- `v1/analise-riscos` 
-- `Categoria Risco técnico: (sobrecompra IFR, divergência IFR, risco na força da tendência)`
-- `Analise de riscos financeiros (HF e Alavancagem)`

---

## 🗓️ Próxima implementação

- 🌟 `analise-riscos`: Estrutural BTC
--Incluir a analise financeira na analise de riscos e considerar o Score no calculo final e alertas

---

# 📌 v1.0.15 - Analise de Riscos - Riscos Financeiro Direto

Completei com sucesso a implementação do sistema de análise de risco financeiro. Veja o status atual:
A versão anterior está com erro, e dados fixo, não funcionou o Scraping
foi tentado varias formas de conseguir os dados na AAVE sem sucesso
mas essa versão agora está buscndo e calculando corretamente
abaixo está o resultado retornado: dados de Exemplo:

{
    "categoria": "Financeiro Direto",
    "score": 8.6,
    "peso": 0.35,
    "principais_alertas": [
        "HF crítico: 1.13",
        "Alavancagem elevada: 3.24x"
    ],
    "financial_overview": {
        "collateral": 495450.26043604,
        "debt": 342416.4245696,
        "nav": 153033.83586644
    },
    "detalhes": {
        "health_factor": {
            "valor": 1.13,
            "classificacao": "Crítico",
            "score": 9.0,
            "peso": 0.8
        },
        "alavancagem": {
            "valor": 3.24,
            "classificacao": "Elevada",
            "score": 7.0,
            "peso": 0.2
        }
    }
}