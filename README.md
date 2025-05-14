# 🚀 BTC Turbo API – v1.0.8

API em FastAPI para cálculo de indicadores técnicos e análise de ciclos do BTC, com deploy Dockerizado via Railway.

---

## 🛰️ Endpoints (Produção)

### 🚀 Cliclos BTC
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

### Descrições Técnicas

- **.DS_Store**: Arquivo utilizado pelo macOS para armazenar atributos personalizados de uma pasta.
- **.env.example**: Arquivo de exemplo contendo variáveis de ambiente necessárias para a configuração e execução do projeto.
- **.gitattributes**: Define atributos específicos para os arquivos em um repositório Git.
- **.gitignore**: Lista de arquivos e diretórios que devem ser ignorados pelo versionamento Git.
- **Dockerfile**: Script para a criação de imagens Docker, útil para a implantação e execução do projeto em contêineres.
- **README.md**: Arquivo de documentação principal do projeto que fornece informações sobre instalação, uso e contribuição.
- **requirements.txt**: Contém uma lista de pacotes Python necessários que devem ser instalados com o `pip`.
- **app/**: Diretório principal do aplicativo contendo os submódulos e scripts do projeto.
  - **__init__.py**: Indica que o diretório é um módulo Python.
  - **config.py**: Script de configuração da aplicação.
  - **dependencies.py**: Definições de dependências que são usadas em várias partes da aplicação.
  - **main.py**: Script principal que inicia a aplicação ou API.
  - **models/**: Contém definições de modelos de dados.
  - **routers/**: Contém os roteadores da API, organizando os endpoints por funcionalidades.
  - **services/**: Implementa lógica de aplicação e integrações de serviços.
  - **utils/**: Fornece funções utilitárias que suportam o funcionamento de outras partes do aplicativo.

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
- Separação clara entre lógica, serviços, e configuração
- `config.py` centralizado via `BaseSettings` e `@lru_cache`
- Dockerfile controlado manualmente (Railway via modo Dockerfile)
- Swagger e OpenAPI prontos para uso
- Uso de query parameters para `username` e `password` (TV)

---

# ⚙️ Diretrizes para próximos desenvolvimentos

- 📚 Cada novo endpoint deve seguir o padrão `routers + services + utils`

## Registro dos routers com prefixo versionado no main
app.include_router(analise_tecnica_emas.router, prefix="/api/v1")

## Nos routers usar assim
@@router.get("/analise-ciclos", 
            summary="Análise de ciclos do BTC", 
            tags=["Ciclos"])

---

## 🗓️ Versão atual 1.0.8 - 13/05/2025 18:00

```text

### 📝 APIs já concluídas e funcionando 100% estáveis

- v1/analise-tecnica
- v1/analise-cliclos
- v1/analise-fundamentos
- v1/analise-riscos (dados mokados)

## 🗓️ Proxima implementação

  - 🌟 **analise-riscos**
  - implementar a coleta e calculo dos riscos
  

### 📝 Melhorias implementadas na versão

- 🌟 **Analise Riscos**
  - Criado o endpoint
  - criado todas as funções e arquivos
  - estamos usando ainda dados Mokados na analise de riscos