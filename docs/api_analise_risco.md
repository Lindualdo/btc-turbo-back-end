# Documentação da API de Análise de Risco Financeiro

Esta documentação descreve detalhadamente o funcionamento da API de Análise de Risco Financeiro do sistema BTC Turbo, que avalia métricas financeiras críticas para operações alavancadas.

## Visão Geral

A API de Análise de Risco Financeiro recupera e processa dados da posição alavancada na plataforma AAVE v3, calculando o nível de risco com base em métricas críticas como Health Factor e alavancagem.

### Endpoint

```
GET /api/v1/risco-financeiro
```

## Processo de Obtenção dos Dados (Input)

A API obtém dados financeiros através de múltiplas fontes, na seguinte ordem de prioridade:

1. **Conexão Web3 Direta** - Conexão direta com os contratos inteligentes AAVE v3 na rede Arbitrum:
   - Consulta o contrato em `0x794a61358D6845594F94dc1DB02A252b5b4814aD`
   - Recupera dados da função `getUserAccountData` para o endereço da carteira

2. **APIs Alternativas** (quando Web3 não está disponível):
   - **Debank API** - API para obtenção de dados de protocolos DeFi
   - **AAVE API Oficial** - API oficial da AAVE para dados de usuários
   - **AAVE API Alternativa** - API secundária da AAVE
   - **AAVE UI API** - API usada pela interface de usuário da AAVE

## Processamento dos Dados (Processo)

### 1. Cálculo dos Valores Básicos

- **Health Factor (HF)** - Obtido diretamente do contrato ou APIs
- **Collateral (Colateral)** - Valor total dos ativos depositados como garantia (em USD)
- **Debt (Dívida)** - Valor total dos empréstimos (em USD)
- **NAV (Net Asset Value)** - Valor líquido dos ativos, calculado como: `Collateral - Debt`
- **Leverage (Alavancagem)** - Calculado como: `Collateral / NAV`

### 2. Pontuação de Risco (Score)

#### Health Factor (peso: 0.7)
- **< 1.0** → 10.0 pontos - "Liquidação Iminente"
- **< 1.2** → 9.0 pontos - "Crítico"
- **< 1.5** → 7.0 pontos - "Elevado"
- **< 2.0** → 5.0 pontos - "Moderado"
- **< 3.0** → 3.0 pontos - "Baixo"
- **≥ 3.0** → 1.0 ponto - "Seguro"

#### Alavancagem (peso: 0.3)
- **> 5.0x** → 10.0 pontos - "Extrema"
- **> 3.0x** → 7.0 pontos - "Elevada"
- **> 2.0x** → 5.0 pontos - "Moderada"
- **> 1.5x** → 3.0 pontos - "Controlada"
- **≤ 1.5x** → 1.0 ponto - "Baixa"

### 3. Cálculo do Resultado Final
- **Score final** = (HF score × 0.7) + (Leverage score × 0.3)
- **Gera alertas** para condições críticas (HF < 1.5 ou alavancagem > 3.0)

## Resultado (Output)

A API retorna um objeto JSON com a seguinte estrutura:

```json
{
  "categoria": "Financeiro Direto",
  "score": 4.2,
  "peso": 0.35,
  "principais_alertas": [
    "Alavancagem elevada: 3.25x"
  ],
  "financial_overview": {
    "collateral": 493822.03,
    "debt": 342412.61,
    "nav": 151409.42
  },
  "detalhes": {
    "health_factor": {
      "valor": 1.12,
      "classificacao": "Crítico",
      "score": 9.0,
      "peso": 0.7
    },
    "alavancagem": {
      "valor": 3.26,
      "classificacao": "Elevada",
      "score": 7.0,
      "peso": 0.3
    }
  }
}
```

## Informações Adicionais

- **Cache**: As consultas são atualizadas a cada 10 minutos para reduzir carga nas APIs.
- **Failover**: O sistema possui mecanismo de failover para garantir a disponibilidade dos dados mesmo se uma fonte falhar.
- **Logging**: Todas as operações e erros são registrados para facilitar a depuração e monitoramento.

## Notas Importantes

- O Health Factor é um indicador crítico que representa a saúde da posição alavancada. Valores abaixo de 1.5 representam riscos significativos de liquidação.
- A Alavancagem é calculada dividindo "Supplied Asset Value" por "Net Asset Value". Valores acima de 3.0 são considerados elevados e indicam maior exposição ao risco.