
# 🚀 BTC Turbo API – v1.0.12

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
    ├── .DS_Store
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
    │   └── analise_tecnica_emas.py
    │   └── analise_riscos.py
    ├── services
    │   ├── __init__.py
    │   ├── btc_analysis.py
    │   ├── fundamentals.py
    │   └── tv_session_manager.py
    │   └── risk_analysis.py
    └── utils
    │     ├── __init__.py
    │     └── ema_utils.py
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

## Registro dos routers com prefixo versionado no main

```python
app.include_router(analise_tecnica_emas.router, prefix="/api/v1")
```

## Nos routers usar assim

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
- `v1/analise-riscos` (sobrecompra IFR, divergência IFR, risco na força da tendência)

---

## 🗓️ Próxima implementação

- 🌟 **analise-riscos**
  - força da tendência

---

# 📄 Documentação: Endpoint de Análise de Tendência e Risco - v1.0.12
Implemententado resultados consolidados de cada indicador da categoria de Risco Técnico no endpoint de análise de riscos. 
Agora, a resposta da API inclui um novo campo indicadores_tecnicos que contém os dados detalhados dos três componentes principais:

Sobrecompra de IFR
Divergência de IFR
Risco da Tendência
O que foi implementado:
Adicionei uma nova estrutura no serviço de análise de riscos que consolida os dados dos indicadores técnicos de forma organizada e intuitiva:

"indicadores_tecnicos": {
  "rsi_sobrecompra": {
    "pontuacao": 2.5,
    "pontuacao_maxima": 5.0,
    "valores": { "1h": 67.2, "4h": 59.1, ... }
  },
  "divergencia_rsi": {
    "pontuacao": 3.0,
    "pontuacao_maxima": 5.0,
    "divergencias": { "4h": { "tipo": "bearish", ... } }
  },
  "risco_tendencia": {
    "pontuacao": 2.0,
    "pontuacao_maxima": 10.0,
    "score_forca_tendencia": 8.0
  }
}
Benefícios da implementação:
Acesso direto aos indicadores chave: Agora é possível acessar diretamente os principais indicadores técnicos sem precisar percorrer a estrutura completa dos componentes

Visualização clara do score de força da tendência: O valor original da força da tendência (antes da inversão para cálculo do risco) está claramente exposto

Organização lógica: Os indicadores estão agrupados por categoria técnica, facilitando a integração com frontends e dashboards

Manutenção da estrutura original: Toda a estrutura existente foi preservada, apenas adicionando informações complementares

Esta implementação melhora significativamente a facilidade de uso da API para análise de riscos, proporcionando um acesso mais direto e claro aos indicadores técnicos mais importantes para a tomada de decisão.