# Documentação do Projeto BTC-Turbo

## 📄 Visão Geral
O projeto **BTC-Turbo** é uma aplicação baseada em FastAPI, hospedada na Railway, desenvolvida para:

- Calcular indicadores técnicos e de ciclos do mercado do Bitcoin
- Consolidar uma pontuação de tendência (de Bear Market a Bull Market)
- Retornar esses dados em formato JSON para consumo por automações no **n8n** ou dashboards

## ⚖️ Arquitetura da Infraestrutura

- **Backend**: FastAPI (Python)
- **Hospedagem**: Railway
- **Integração**: n8n via HTTP Requests
- **Coleta de dados**:
  - TradingView via `tvDatafeed`
  - Indicadores internos calculados localmente
  - Realized Price com valor fixo (temporário)

## 📂 Estrutura de Diretórios do Projeto (Git)

```
btc_turbo/
├── main.py                  # Inicializa a API e inclui os routers
├── requirements.txt         # Dependências do projeto
├── Dockerfile               # Build para Railway
├── app/
│   ├── __init__.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── btc_emas.py      # Rota /btc-emas
│   │   └── btc_cycles.py    # Rota /btc-cycles
│   ├── services/
│   │   ├── __init__.py
│   │   └── btc_analysis.py  # Lógica dos indicadores (200D EMA, Realized Price, etc.)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── ema_utils.py     # Cálculo de EMAs
│   └── models/
│       ├── __init__.py
│       └── btc_models.py    # (Reservado para schemas futuros)
```

## 📊 Indicadores Atuais Implementados

### 1. `/btc-emas`
- Calcula EMAs 17, 34, 144, 305, 610 para os timeframes: 15m, 1h, 4h, 1d, 1w
- Retorna também preço e volume atual

### 2. `/btc-cycles`
Consolida 2 indicadores de ciclo:
- **BTC vs 200D EMA** (peso: 25%)
- **BTC vs Realized Price** (peso: 25%, valor fixo por enquanto)

Retorna:
- Pontuação individual de cada indicador
- Pontuação final normalizada (0 a 10)
- Classificação do mercado
- Estratégia sugerida
- Destaques

## ✅ Status Atual

- Estrutura de projeto modular implementada e validada
- API implantada com sucesso na Railway
- Testes via n8n realizados com sucesso
- Indicadores básicos de ciclo operacionais
- Integração com TradingView funcional (via username/senha)

## ⌚ Pendências / Limitações

- **Realized Price** é fixo manualmente (sem scraping nem API paga)
- **Demais indicadores de ciclo ainda não implementados**:
  - Puell Multiple
  - Tendência da Dominância do BTC
  - Macroambiente (liquidez e juros)
- **Sem dados on-chain em tempo real via API confiável gratuita**

## 🔄 Próximos Passos

1. **Escolher uma fonte gratuita para indicadores on-chain**:
   - CoinMetrics ou Messari (ambas com APIs gratuitas)
   - Implementar fallback com valores fixos atualizados periodicamente, se necessário

2. **Implementar novo endpoint**:
   - `/btc-puell` com integração via CoinMetrics ou similar

3. **Expandir `/btc-cycles`**:
   - Adicionar os demais indicadores (com pesos definidos no documento oficial)

4. **Exportar para Notion**:
   - Opcional: envio automático de resultados para base de dados externa ou dashboard

5. **Análise de Fundamentos**:
   - Planejada como próxima fase (on-chain, supply, atividade da rede)

---

Essa documentação pode ser mantida no repositório como `README.md` ou `docs/projeto.md`. Deseja que eu gere o arquivo para commit?

