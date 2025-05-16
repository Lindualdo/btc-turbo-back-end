# API de Análise de Risco

## Fontes de Dados
- **Fonte principal:** Web3 direto nos contratos AAVE v3 na rede Arbitrum
- **Fallbacks:** Debank API, AAVE API Oficial, AAVE API Alternativa, AAVE UI API

## Variáveis
### Recebidas Diretamente
- Health Factor: Indicador de saúde da posição (obtido via contratos/APIs)
- Total Collateral USD: Valor total dos ativos depositados
- Total Debt USD: Valor total dos empréstimos

### Calculadas
- Net Asset Value (NAV): Total Collateral - Total Debt
- Leverage (Alavancagem): Total Collateral / NAV

## Cálculo de Risco
- Pontuação Health Factor (peso 0.7): 1-10 baseado em faixas de valores
- Pontuação Alavancagem (peso 0.3): 1-10 baseado em faixas de valores
- Pontuação Final: (HF_score * 0.7) + (Leverage_score * 0.3)

## Exemplo de Resposta
```json
{
  "categoria": "Financeiro Direto",
  "score": 4.2,
  "peso": 0.35,
  "principais_alertas": ["HF crítico: 1.12", "Alavancagem elevada: 3.26x"],
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