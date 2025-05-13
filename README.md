# 🚀 BTC Turbo API – v1.0.5

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
    ├── services
    │   ├── __init__.py
    │   ├── btc_analysis.py
    │   ├── fundamentals.py
    │   └── tv_session_manager.py
    └── utils
        ├── __init__.py
        └── ema_utils.py
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

## 🔧 Padres Técnicos

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
app.include_router(analise_ciclos.router, prefix="/api/v1")
app.include_router(analise_fundamentos.router, prefix="/api/v1")

## Nos routers usar assim
@@router.get("/analise-ciclos", 
            summary="Análise de ciclos do BTC", 
            tags=["Ciclos"])

---

## 🗓️ Versão atual 1.0.5 - 13/05/2025 08:00

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

  ### 📝 Funcionamento das APIs - Inf. importantes

  - 🌟 **analise-cilcos**
  - Alguns indicadres estamos buscando em uma tabela no Notion
  - Os demanis indicadores, são buscado direto nas fontes oficiais da especificação via API
  - Futuramente tentaremos outras abordagens, tipo scraping


## 🗓️ Proxima implementação

  - 🌟 **analise-fundamentos**
  - Reregra está implementadade de forma fixa no codigo
  - Ao implementar, seguir o que foi desenvolvido na API analise-cilcos > Puell Multiple
  - Acessar a mesma base de dados do Notion 
  - Ler a documentação com as regras, na pasta /app/documentacao/analise-fundamentos.md