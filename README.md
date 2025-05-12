# 🚀 BTC Turbo API – v1.0.3

API em FastAPI para cálculo de indicadores técnicos e análise de ciclos do BTC, com deploy Dockerizado via Railway.

---

## 🛰️ Endpoints (Produção)

### 🚀 Cliclos BTC
```
GET /api/v1/btc-cycles/btc-cycles
```

### 🛈 EMAs BTC
```
GET /api/v1/btc-emas/analyse-tecnica-emas
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

## 🏗️ Arquitetura do Projeto

```plaintext
/app/
   main.py          # Instância FastAPI e registrando routers
   config.py        # Configuração da aplicação (pydantic)
   routers/         # Endpoints organizados por tema
   btc_emas.py
   btc_cycles.py
   dependencies.py  # Lógica reutilizável (ex: calcular_emas)
   services/        # Serviços e integrações (ex: TradingView)
requirements.txt
Dockerfile
.env.example
README.md
```

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

## 🔧 Padres Técnicos

- APIs organizadas por domínio (`/btc-emas`, `/btc-cycles`)
- Separação clara entre lógica, serviços, e configuração
- `config.py` centralizado via `BaseSettings` e `@lru_cache`
- Dockerfile controlado manualmente (Railway via modo Dockerfile)
- Swagger e OpenAPI prontos para uso
- Uso de query parameters para `username` e `password` (TV)

---

## ⚙️ Diretrizes para próximos desenvolvimentos

- 📚 Cada novo endpoint deve seguir o padrão `routers + services + utils`
- ⚠️ Nunca versionar `.env` ⚠️ usar apenas `.env.example`
- 🔧 Adicionar testes automatizados para endpoints críticos
- 🚀 Refatorar chamadas ao TradingView para serem assíncronas (futuro)
- 🤖 Toda nova versão deve ser marcada por tag (`v1.x.x`)

---

## 🗓️ Versão 04/04/25 - 18:30 - v1.0.2

```text

### 📝 Melhorias implementadas

- 🌟 **Gerenciamento de sessão persistente**
  - Reutilização de instância ativa (`tv`) sem recriar login desnecessariamente
  - Logs indicam o reaproveitamento da sessão de forma clara
- 🌟 **Logs de execução aprimorados**
  - Feedback visual detalhado no console: emoji + descrição clara do fluxo
  - Logs incluem ID da sessão, status de login, e origem dos dados
- 🌟 **Mensagens de erro mais informativas**
  - Ao falhar o login, o erro real da biblioteca `tvDatafeed` é mostrado
- 🌟 **Validação de credenciais configurada**
  - Caso `username` ou `password` estejam ausentes, impede fallback silencioso


## 🗓️ Versão atual - 04/04/25 - 21:00 - 1.0.3 


### 🎯 Funcionalidades Implementadas

### 🚦 Endpoint `/api/v1/analyse-tecnica-emas`

- Análise técnica individual por timeframe com:
  - Score de 0 a 10
  - Classificação textual (🔴, 🟡, 🔶, ⚪)
  - Observação explicativa (quando houver desalinhamento ou fraqueza)
- Cálculo **consolidado multiplot** com pesos:
  - `1w` (50%), `1d` (25%), `4h` (15%), `1h` (10%)
  - Saída com score, classificação final e racional da fórmula
- Endpoint renomado de `/btc-emas` para `/analyse-tecnica-emas`

---

## 📈 Próximos Endpoints v1 (a desenvolver)

### 🟡 Análise Técnica
- `/api/v1/analyse-tecnica-ifrs`

### 🚀 Fundamentos On-Chain
- `/api/v1/analyse-fundamentos`

### 🟢 Índicadores de Risco
- `/api/v1/analyse-riscos`

---

**Versão estável e pronta para integração com n8n e Notion.**

---


---

### Estrutura de Pastas e Arquivos do BTC Turbo

```plaintext
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
    ├── services
    │   ├── __init__.py
    │   ├── btc_analysis.py
    │   ├── fundamentals.py
    │   └── tv_session_manager.py
    └── utils
        ├── __init__.py
        └── ema_utils.py
```

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

