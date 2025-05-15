# 🚀 BTC Turbo API – v1.0.10

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

### 📝 APIs já concluídas e funcionando 100% estáveis

- v1/analise-tecnica
- v1/analise-cliclos
- v1/analise-fundamentos
- v1/analise-riscos (ifr, divergencia ifr, força da tendecia)

## 🗓️ Proxima implementação

  - 🌟 **analise-riscos**
  - força da tendencia


# 📄 Documentação: Endpoint de Análise de Tendência e Risco - v 1.0.11

## 🔍 Visão Geral
O endpoint `/api/v1/analise-tendencia-risco` fornece uma análise detalhada do risco baseado na força da tendência atual do Bitcoin.  
Este componente inverte o score de força técnica para calcular um nível de risco, permitindo decisões de investimento mais seguras.

---

## ⚙️ Especificações Técnicas

### 📌 Endpoint
GET /api/v1/analise-tendencia-risco


### 📥 Resposta
```json
{
  "componente": "Análise de Tendência",
  "pontuacao": 2.5,
  "score_forca_tendencia": 7.5,
  "pontuacao_maxima": 10.0,
  "classificacao": "Monitorar",
  "timeframes": { ... },
  "alertas": [ ... ],
  "racional": "...",
  "detalhes": { ... },
  "classificacao_detalhada": { ... },
  "interpretacao_atual": { ... }
}
🧩 Campos Principais
pontuacao: Nível de risco calculado (0-10)

score_forca_tendencia: Score original de força técnica das EMAs antes da inversão

classificacao: Categoria de risco qualitativa

timeframes: Detalhes por período de análise

alertas: Avisos específicos baseados no nível de risco

interpretacao_atual: Recomendações de ação baseadas no nível de risco

🧮 Metodologia de Cálculo
O sistema obtém o score consolidado de força da tendência do endpoint /api/v1/analise-tecnica-emas.

O score de risco é calculado com a fórmula:

Risco = 10 - Score de Força
O resultado é classificado em 5 níveis:

Faixa de Risco	Alerta	Interpretação
0.0 - 1.9	✅ Nenhum	Estrutura técnica saudável
2.0 - 3.9	⚠️ Monitorar	Pequenos sinais de fraqueza
4.0 - 5.9	🟠 Alerta Moderado	Estrutura comprometida
6.0 - 7.9	🔴 Alerta Crítico	Provável reversão
8.0 - 10.0	🚨 Alerta Máximo	Colapso técnico estrutural

🚀 Implementação
O serviço utiliza detecção automática de ambiente para funcionar corretamente tanto em desenvolvimento local quanto em produção no Railway:

# Detecta o ambiente e configura a URL base corretamente
is_production = os.environ.get("RAILWAY_ENVIRONMENT") == "production"
base_url = "https://btc-turbo-api-production.up.railway.app/api/v1" if is_production else f"http://localhost:{settings.PORT}/api/v1"
🧠 Uso Recomendado
Este indicador deve ser utilizado como parte de uma análise técnica mais ampla para:

Avaliar a saúde da tendência atual
Gerenciar exposição ao risco
Determinar níveis apropriados de alavancagem
Identificar momentos ideais para entrada e saída de posições

📝 Notas Adicionais
O cálculo inverte intencionalmente o score para que valores altos representem maior risco.
Cada nível de risco vem com recomendações específicas de gerenciamento de capital.
A análise abrange múltiplos timeframes para uma visão abrangente do mercado.
