```markdown
# BTC Hold Alavancado - Sistema de Score

## 📊 Estrutura do Sistema

```
BLOCO ÚNICO - Hold Alavancado Score
├── Ciclo (50%)
│   ├── MVRV Z-Score (25%)
│   └── Realized Price Ratio (25%)
├── Momentum (30%)
│   ├── RSI Semanal (15%)
│   ├── Funding Rates (10%)
│   └── Open Interest Change 30D (5%)
└── Risco (20%)
    ├── Distância do Liquidation (10%)
    ├── Health Factor AAVE (5%)
    └── Exchange Netflow 7D (5%)
```

---

## 🎯 Escala de Classificação (0-10)

| Score | Classificação | Descrição |
|-------|--------------|-----------|
| 0-2 | **Crítico** | Risco extremo, ação imediata |
| 2-4 | **Ruim** | Condições desfavoráveis |
| 4-6 | **Neutro** | Mercado equilibrado |
| 6-8 | **Bom** | Condições favoráveis |
| 8-10 | **Ótimo** | Oportunidade excepcional |

---

## 📈 1. CICLO (50% do peso total)

### MVRV Z-Score (25%)
**Fórmula**: `(Market Value - Realized Value) / Std Dev`
**Fonte**: Glassnode, CryptoQuant

| Z-Score | Score | Classificação | Observação |
|---------|-------|--------------|------------|
| < 0 | 9-10 | Ótimo | Fundo histórico, máxima oportunidade |
| 0-2 | 7-8 | Bom | Subvalorizado, boa entrada |
| 2-4 | 5-6 | Neutro | Valor justo |
| 4-6 | 3-4 | Ruim | Sobrevalorizado |
| > 6 | 0-2 | Crítico | Topo histórico provável |

### Realized Price Ratio (25%)
**Fórmula**: `Preço BTC / Realized Price`
**Fonte**: Glassnode, LookIntoBitcoin

| Ratio | Score | Classificação | Observação |
|-------|-------|--------------|------------|
| < 0.7 | 9-10 | Ótimo | Abaixo do custo médio da rede |
| 0.7-1.0 | 7-8 | Bom | Próximo ao custo base |
| 1.0-1.5 | 5-6 | Neutro | Lucro moderado da rede |
| 1.5-2.5 | 3-4 | Ruim | Lucro elevado, cautela |
| > 2.5 | 0-2 | Crítico | Lucro extremo, topo provável |

---

## 📊 2. MOMENTUM (30% do peso total)

### RSI Semanal (15%)
**Fonte**: TradingView, Glassnode

| RSI | Score | Classificação | Observação |
|-----|-------|--------------|------------|
| < 30 | 9-10 | Ótimo | Oversold, reversão provável |
| 30-45 | 7-8 | Bom | Momentum bearish esgotado |
| 45-55 | 5-6 | Neutro | Equilíbrio |
| 55-70 | 3-4 | Ruim | Sobrecompra moderada |
| > 70 | 0-2 | Crítico | Sobrecompra extrema |

### Funding Rates - Média 7D (10%)
**Fonte**: Coinglass, Glassnode

| Funding Rate | Score | Classificação | Observação |
|--------------|-------|--------------|------------|
| < -0.05% | 9-10 | Ótimo | Shorts pagando, bullish |
| -0.05% a 0% | 7-8 | Bom | Mercado equilibrado bearish |
| 0% a 0.02% | 5-6 | Neutro | Normal, sem pressão |
| 0.02% a 0.1% | 3-4 | Ruim | Longs pagando alto |
| > 0.1% | 0-2 | Crítico | Euforia, correção iminente |

### Open Interest Change 30D (5%)
**Fórmula**: `(OI Atual - OI 30D atrás) / OI 30D atrás × 100`
**Fonte**: Coinglass, CryptoQuant

| OI Change % | Score | Classificação | Observação |
|-------------|-------|--------------|------------|
| < -30% | 9-10 | Ótimo | Capitulação, fundo próximo |
| -30% a -10% | 7-8 | Bom | Redução saudável de leverage |
| -10% a +20% | 5-6 | Neutro | Crescimento normal |
| +20% a +50% | 3-4 | Ruim | Alavancagem crescente |
| > +50% | 0-2 | Crítico | Excesso de especulação |

---

## ⚠️ 3. RISCO (20% do peso total)

### Distância do Liquidation (10%)
**Fórmula**: `((Preço Atual - Preço Liquidação) / Preço Atual) × 100`

| Distância % | Score | Classificação | Observação |
|-------------|-------|--------------|------------|
| > 50% | 9-10 | Ótimo | Muito seguro |
| 30-50% | 7-8 | Bom | Margem confortável |
| 20-30% | 5-6 | Neutro | Aceitável com monitoramento |
| 10-20% | 3-4 | Ruim | Risco elevado |
| < 10% | 0-2 | Crítico | Liquidação iminente |

### Health Factor AAVE (5%)

| Health Factor | Score | Classificação | Observação |
|---------------|-------|--------------|------------|
| > 2.0 | 9-10 | Ótimo | Ultra seguro |
| 1.5-2.0 | 7-8 | Bom | Posição saudável |
| 1.3-1.5 | 5-6 | Neutro | Monitorar |
| 1.1-1.3 | 3-4 | Ruim | Ajuste necessário |
| < 1.1 | 0-2 | Crítico | Risco de liquidação |

### Exchange Netflow 7D (5%)
**Fórmula**: `Inflow - Outflow` (média 7 dias)
**Fonte**: CryptoQuant, Glassnode

| Netflow | Score | Classificação | Observação |
|---------|-------|--------------|------------|
| < -50k BTC | 9-10 | Ótimo | Forte acumulação, bullish |
| -50k a -10k | 7-8 | Bom | Saída líquida, positivo |
| -10k a +10k | 5-6 | Neutro | Equilíbrio |
| +10k a +50k | 3-4 | Ruim | Pressão vendedora |
| > +50k BTC | 0-2 | Crítico | Dump iminente |

---

## 🧮 Exemplo de Cálculo Real

### Dados Atuais:
- MVRV Z-Score: 4.5
- BTC vs EMA 200D: +15%
- RSI Semanal: 66
- Funding Rates 7D: 0.02%
- Distância Liquidação: 8.5%
- Health Factor: 1.09

### Cálculos:

**1. CICLO (50%)**
- MVRV Z-Score: 4.5 → Score 3.5 × 0.25 = **0.88**
- Realized Price Ratio: 1.8 → Score 4.0 × 0.25 = **1.00**
- **Subtotal Ciclo: 1.88/5.0**

**2. MOMENTUM (30%)**
- RSI Semanal: 66 → Score 3.5 × 0.15 = **0.53**
- Funding Rates: 0.02% → Score 5.0 × 0.10 = **0.50**
- Open Interest Change: +35% → Score 3.0 × 0.05 = **0.15**
- **Subtotal Momentum: 1.18/3.0**

**3. RISCO (20%)**
- Distância Liquidação: 8.5% → Score 1.5 × 0.10 = **0.15**
- Health Factor: 1.09 → Score 1.0 × 0.05 = **0.05**
- Exchange Netflow: +25k BTC → Score 3.0 × 0.05 = **0.15**
- **Subtotal Risco: 0.35/2.0**

### **SCORE FINAL: 3.41/10 (RUIM)**

---

## 💰 Gestão por Kelly Criterion

### Fórmula Adaptada:
```
f* = (p × b - q) / b × fator_segurança

Onde:
- f* = % do capital para alocar
- p = probabilidade de ganho = Score/10
- b = odds (estimado em 2:1 para BTC)
- q = probabilidade de perda = 1-p
- fator_segurança = 0.25 (máximo 25% Kelly)
```

### Tabela de Alocação:

| Score Final | Classificação | % Kelly | Ação Recomendada |
|-------------|--------------|---------|------------------|
| 0-2 | Crítico | 0% | Fechar posição |
| 2-4 | Ruim | 10% | Reduzir drasticamente |
| 4-6 | Neutro | 25% | Posição conservadora |
| 6-8 | Bom | 50% | Aumentar gradualmente |
| 8-10 | Ótimo | 75% | Posição máxima |

---

## 🎯 Modelo de Alocação Core-Satellite

### Estrutura Recomendada:
```
PATRIMÔNIO TOTAL BTC
├── Core Position (50%) - HOLD PURO
│   ├── Nunca alavancado
│   ├── Cold wallet / CEX segura
│   └── Ganho garantido no bull market
└── Satellite Position (50%) - HOLD ALAVANCADO
    ├── Aplicar sistema de score
    ├── Depositar em AAVE conforme Kelly
    └── Ajustes dinâmicos
```

### Por que 50/50?
1. **Proteção**: Nunca perde todo patrimônio
2. **Upside**: Ainda captura ganhos amplificados
3. **Psicológico**: Permite dormir tranquilo
4. **Flexibilidade**: Pode ajustar em extremos

### Aplicação Prática com Kelly:

**Exemplo: Patrimônio de 2 BTC**
- Core: 1 BTC (sempre HOLD)
- Satellite: 1 BTC (para estratégia)

| Score | Kelly % | BTC em AAVE | Empréstimo Máx* | Exposição Total | Alavancagem |
|-------|---------|-------------|-----------------|-----------------|-------------|
| 0-2   | 0%      | 0 BTC       | $0              | 1.00 BTC        | 1.00x       |
| 2-4   | 10%     | 0.10 BTC    | $7,500          | 1.07 BTC        | 1.07x       |
| 4-6   | 25%     | 0.25 BTC    | $18,750         | 1.17 BTC        | 1.17x       |
| 6-8   | 50%     | 0.50 BTC    | $37,500         | 1.35 BTC        | 1.35x       |
| 8-10  | 75%     | 0.75 BTC    | $56,250         | 1.53 BTC        | 1.53x       |

*Assumindo LTV 70% e mantendo Health Factor > 1.3

### Cálculo de Posição Ideal:
```
1. Capital Satellite = Patrimônio Total × 50%
2. BTC para AAVE = Capital Satellite × Kelly%
3. Empréstimo Máximo = (BTC em AAVE × Preço BTC × 70%) / 1.3
4. Exposição Total = Core + Satellite + (Empréstimo/Preço BTC)
```

### Regras de Segurança:
1. **NUNCA** alavancar a Core Position
2. **SEMPRE** manter Health Factor > 1.3
3. **REBALANCEAR** quando score mudar de faixa
4. **PARAR** alavancagem se score < 2

---

## 📋 Padrão de Saída JSON

```json
{
  "timestamp": "2025-05-25T14:30:00Z",
  "score_final": 3.41,
  "classificacao_geral": "Ruim",
  "kelly_allocation": "10%",
  "acao_recomendada": "Manter posição mínima, monitorar closely",
  "blocos": {
    "ciclo": {
      "peso": "50%",
      "score": 1.88,
      "indicadores": [
        {
          "nome": "MVRV Z-Score",
          "fonte": "Glassnode",
          "valor": 4.5,
          "score": 3.5,
          "score_ponderado": 0.88,
          "classificacao": "Ruim"
        },
        {
          "nome": "Realized Price Ratio",
          "fonte": "CryptoQuant",
          "valor": 1.8,
          "score": 4.0,
          "score_ponderado": 1.00,
          "classificacao": "Ruim"
        }
      ]
    },
    "momentum": {
      "peso": "30%",
      "score": 1.18,
      "indicadores": [
        {
          "nome": "RSI Semanal",
          "fonte": "TradingView",
          "valor": 66,
          "score": 3.5,
          "score_ponderado": 0.53,
          "classificacao": "Ruim"
        },
        {
          "nome": "Funding Rates 7D",
          "fonte": "Coinglass",
          "valor": "0.02%",
          "score": 5.0,
          "score_ponderado": 0.50,
          "classificacao": "Neutro"
        },
        {
          "nome": "Open Interest Change 30D",
          "fonte": "Coinglass",
          "valor": "+35%",
          "score": 3.0,
          "score_ponderado": 0.15,
          "classificacao": "Ruim"
        }
      ]
    },
    "risco": {
      "peso": "20%",
      "score": 0.35,
      "indicadores": [
        {
          "nome": "Distância Liquidação",
          "fonte": "AAVE",
          "valor": "8.5%",
          "score": 1.5,
          "score_ponderado": 0.15,
          "classificacao": "Crítico"
        },
        {
          "nome": "Health Factor",
          "fonte": "AAVE",
          "valor": 1.09,
          "score": 1.0,
          "score_ponderado": 0.05,
          "classificacao": "Crítico"
        },
        {
          "nome": "Exchange Netflow 7D",
          "fonte": "CryptoQuant",
          "valor": "+25k BTC",
          "score": 3.0,
          "score_ponderado": 0.15,
          "classificacao": "Ruim"
        }
      ]
    }
  }
}
```

---

## 🚨 Alertas Automáticos

| Condição | Alerta | Ação |
|----------|--------|------|
| Score < 2 | **CRÍTICO** | Zerar alavancagem imediatamente |
| HF < 1.15 | **PERIGO** | Adicionar colateral ou pagar dívida |
| Distância Liq < 15% | **ATENÇÃO** | Revisar posição |
| Funding > 0.1% | **EUFORIA** | Considerar redução |
| MVRV > 6 | **TOPO** | Preparar saída gradual |

---

## 📝 Notas Importantes

1. **Frequência de Cálculo**: Mínimo 2x ao dia (00h e 12h UTC)
2. **Stop Loss**: Se Score < 2 por 24h consecutivas
3. **Rebalanceamento**: Ajustar quando score mudar de faixa
4. **Backtesting**: Este modelo deve ser validado com dados históricos
5. **Ajuste Dinâmico**: Os pesos podem ser otimizados com ML
6. **Core Position**: NUNCA deve ser alavancada
7. **Disciplina**: Seguir o sistema independente de emoções

---

*Última atualização: 25/05/2025 as 15:08*
```
