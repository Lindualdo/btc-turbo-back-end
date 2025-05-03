
# 🧠 BTC Turbo API — v1.1.0

API em FastAPI para cálculo de indicadores técnicos e análise de ciclos do BTC, com deploy Dockerizado via Railway.

---

## 🌐 Endpoints (Produção)

### 🔁 Ciclos BTC
```
GET /api/v1/btc-cycles/btc-cycles?username=SEU_USER&password=SUA_SENHA
```

### 📊 EMAs BTC
```
GET /api/v1/btc-emas/btc-emas?username=SEU_USER&password=SUA_SENHA
```

### 🩺 Health Check
```
GET /health
```

### ⚙️ Configurações Ativas
```
GET /config
```

### 📘 Swagger UI (Documentação)
```
GET /docs
```

### 🧾 OpenAPI JSON
```
GET /openapi.json
```

---

## 🧱 Arquitetura do Projeto

```
.
├── app/
│   ├── main.py             # Instância FastAPI e registro de routers
│   ├── config.py           # Configurações da aplicação (pydantic)
│   ├── routers/            # Endpoints organizados por tema
│   │   ├── btc_emas.py
│   │   ├── btc_cycles.py
│   ├── utils/              # Lógica reutilizável (ex: calcular_emas)
│   └── services/           # Serviços e integrações (ex: TradingView)
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

---

## 📦 Dependências principais

- `FastAPI` / `Uvicorn`
- `tvDatafeed` (via GitHub: `rongardF`)
- `pandas`
- `notion-client`
- `pydantic-settings >= 2.0.0`

---

## 🧠 Padrões Técnicos

- APIs organizadas por domínio (`/btc-emas`, `/btc-cycles`)
- Separação clara entre lógica, serviços, e configuração
- `config.py` centralizado via `BaseSettings` e `@lru_cache`
- Dockerfile controlado manualmente (Railway via modo Dockerfile)
- Swagger e OpenAPI prontos para uso
- Uso de query parameters para `username` e `password` (TV)

---

## 🚧 Diretrizes para próximos desenvolvimentos

- ⚙️ Cada novo endpoint deve seguir o padrão `routers + services + utils`
- 🔐 Nunca versionar `.env` — usar apenas `.env.example`
- 🧪 Adicionar testes automatizados para endpoints críticos
- 📉 Refatorar chamadas ao TradingView para serem assíncronas (futuro)
- 🔁 Toda nova versão deve ser marcada por tag (`v1.x.x`)

---

## 🧊 Versão atual

```text
Versão congelada: v1.1.0
Status: ✅ Estável
Base: Refatoração pós-v1.0.0 com EMAs e Ciclos funcionando
```
