**Documentação Consolidada do Projeto**

---

## 1. Arquivo: `main.py`

### Observações Atuais

* Ponto de entrada minimalista em FastAPI.
* Registro de routers sem prefixos de versão ou tags OpenAPI.
* Ausência de endpoints de saúde, métricas e middlewares (CORS, logging, tratamento de exceções).
* Sem eventos de startup/shutdown configurados.

### Melhorias Sugeridas

1. **Metadados da API**: adicionar `title`, `description`, `version`, `contact`, `license` na instância FastAPI.
2. **Versionamento de Rotas**: prefixar com `/api/v1` e definir tags para cada router.
3. **Health Check & Métricas**: criar `GET /health`, integrar Prometheus (`starlette_exporter`) ou logging detalhado.
4. **Middlewares**: configurar CORS, logger global, tratamento centralizado de exceções.
5. **Eventos de Ciclo de Vida**: implementar `@app.on_event("startup")` e `@app.on_event("shutdown")` para inicializar e fechar recursos.
6. **Customização da Documentação**: ajustar `docs_url`, `redoc_url`, organizar tags.
7. **Segurança Básica**: considerar autenticação (API Key, OAuth2) se aplicável.
8. **Docstring**: incluir comentário de uso e propósito do arquivo.

---

## 2. Arquivo: `app/routers/btc_emas.py`

### Observações Atuais

* Credenciais `username`/`password` recebidas via query params, expondo dados sensíveis.
* Instanciação do cliente `TvDatafeed` dentro do endpoint.
* Ausência de `response_model`, `summary`, `tags` no decorator.
* Tratamento de erros genérico (retorna 200 mesmo em falha).
* Sem cache para dados históricos.

### Melhorias Sugeridas

1. **Segurança**: mover credenciais para variáveis de ambiente ou Secret Manager.
2. **Dependências**: instanciar `TvDatafeed` em evento de startup e injetar via `Depends`.
3. **Models Pydantic**: criar schemas para EMAs e usar `response_model` para documentação.
4. **Status Code**: usar `HTTPException` para falhas com código 4xx/5xx.
5. **Cache**: implementar cache (Redis ou lru\_cache) para minimizar chamadas a TradingView.
6. **Logging**: adicionar logs para cada período processado.
7. **Testes**: criar unit tests simulando `tv.get_hist`.
8. **API Versioning**: prefixar rota com `/api/v1/btc-emas`.

---

## 3. Arquivo: `app/routers/btc_cycles.py`

### Observações Atuais

* Exposição de credenciais via query params.
* Lógica de negócios implementada no router, não no service layer.
* Pesos hardcoded (`pesos_personalizados`) no código.
* Ausência de Pydantic models e documentação OpenAPI.
* Tratamento de erro insuficiente e sem uso de `HTTPException`.
* Sem cache ou logs de métricas.

### Melhorias Sugeridas

1. **Credenciais**: usar env vars ou Secret Manager.
2. **Service Layer**: mover lógica de consolidação e cálculos para `app/services`.
3. **Configuração Externa**: externalizar pesos em arquivo de configuração (JSON/YAML) ou env vars.
4. **Schemas**: definir Pydantic models para `dados_individuais`, `dados_consolidados` e `resumo_executivo`.
5. **Cache e Logging**: usar cache para resultados pesados, registrar início/fim de requisição.
6. **Erros**: lançar `HTTPException` com detalhes apropriados.
7. **Versionamento**: usar prefixo `/api/v1/btc-cycles`.
8. **Testes**: desenvolver testes de integração e unitários para cálculo de pontuações.

---

## 4. Arquivo: `app/services/btc_analysis.py`

### Observações Atuais

* Mistura de coleta de dados (TradingView, Notion) e lógica de negócio num único módulo.
* `Realized Price` fixo no código em vez de configurável.
* Pesos e limites de pontuação hardcoded.
* Tratamento de erros genérico, sem propagação de exceções.
* Retornos formatados (strings) em vez de valores numéricos puros.
* Sem anotações de tipos ou docstrings explicativas.

### Melhorias Sugeridas

1. **Separação de Responsabilidades**:

   * `coleta_clientes.py`: inicialização de clientes externos (TradingView, Notion).
   * `indicadores.py`: cálculos puros de indicadores.
2. **Configurações**: usar `pydantic.BaseSettings` para credenciais, IDs Notion, pesos e limites.
3. **Pydantic Models**: definir schemas para cada indicador e para resposta consolidada.
4. **Formatação na Camada de Router**: manter números na service e formatar no router.
5. **Erro e Logging**: capturar exceções específicas, usar `structlog` ou `logging`.
6. **Caching**: implementar cache para consultas externas.
7. **Type Hints & Docstrings**: detalhar parâmetros, retornos e fórmulas.
8. **Testes Paramétricos**: validar algoritmos de pontuação com pytest.

---

## 5. Arquivo: `app/utils/ema_utils.py`

### Observações Atuais

* Função `calcular_emas` modifica DataFrame original e carece de validação.
* Sem docstrings ou tratamento de exceções.
* Sem testes.

### Melhorias Sugeridas

1. **Docstrings & Type Hints**: detalhar args e retorno.
2. **Validação de Esquema**: verificar existência de coluna `close`.
3. **Imutabilidade**: operar em `df.copy()` em vez de modificar in-place.
4. **Erro e Logging**: capturar erros de pandas e logar contexto.
5. **Cache**: considerar cache para DataFrames idênticos.
6. **Unit Tests**: criar testes para vários cenários e erros esperados.

---

## 6. Diretório: `app/models`

### Observações Atuais

* Diretório existe, mas sem arquivos de schemas.

### Melhorias Sugeridas

1. **Definir Schemas Pydantic**:

   * `EMAResponse`, `CycleIndicator`, `ConsolidatedResponse`, `ResumoExecutiveItem`.
2. **Reutilização**: usar models em routers e services para garantir consistência.
3. **OpenAPI**: models permitem documentação automática completa.

---

## 7. Arquivo: `requirements.txt`

### Observações Atuais

* Dependências sem versões fixas.
* Instalação direta de Git para `tvdatafeed` sem fixar commit.
* Sem dependências de desenvolvimento (linters, testes, formatação).

### Melhorias Sugeridas

1. **Pinagem de Versões**: travar versões exatas para produção.
2. **Dev Requirements**: criar `dev-requirements.txt` com pytest, black, flake8, mypy.
3. **Repositório Git**: fixar `@<commit>` ao instalar `tvdatafeed`.
4. **Constraints File**: usar `pip-compile` para gerar lista definitiva.

---

## 8. Arquivo: `Dockerfile`

### Observações Atuais

* Base image sem digest, context root sem `WORKDIR`, ausência de `.dockerignore`.
* Duplo `pip install` e execução como root.
* Sem limpeza adequada do apt cache.
* Sem labels, usuário não-root ou healthcheck.

### Melhorias Sugeridas

1. **WORKDIR & dockerignore**: definir `WORKDIR /app`; criar `.dockerignore`.
2. **Base Image Pinada**: usar digest ou tag específica.
3. **Multi-stage Build**: separar builder e runtime.
4. **Unificar pip install**: instalar tudo em um único comando e remover duplicações.
5. **User Non-Root**: criar e usar usuário sem privilégios.
6. **Labels & Metadados**: adicionar `LABEL maintainer`, versão e descrição.
7. **Healthcheck**: incluir instrução `HEALTHCHECK` para monitoramento.

---

**Próximos Passos**

1. Revisar estas recomendações e priorizar implementações.
2. Definir padrões de Git (branching, commits, PRs) e CI/CD.
3. Migrar configurações sensíveis para env vars e secrets manager.
4. Estruturar testes automatizados e pipeline de qualidade de código.

*Este documento serve como base para alinharmos padrões e metodologia antes de avançar com o desenvolvimento das próximas APIs.*
