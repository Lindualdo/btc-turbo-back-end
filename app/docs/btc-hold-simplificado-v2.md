# BTC Hold Alavancado - Sistema de Score v2.0

## 📊 Estrutura do Sistema Atualizado

```
BLOCO ÚNICO - Hold Alavancado Score
├── Ciclo (40%)
│   ├── MVRV Z-Score (20%)
│   ├── Realized Price Ratio (15%)
│   └── Puell Multiple (5%)
├── Momentum (25%)
│   ├── RSI Semanal (10%)
│   ├── Funding Rates 7D (8%)
│   ├── Open Interest Change 30D (4%)
│   └── Long/Short Ratio (3%)
├── Risco (15%)
│   ├── Distância do Liquidation (6%)
│   ├── Health Factor AAVE (4%)
│   ├── Exchange Netflow 7D (3%)
│   └── Stablecoin Supply Ratio (2%)
└── Técnico (20%)
    ├── Posição vs EMA 200 (8%)
    ├── Estrutura de EMAs (7%)
    └── Padrões Gráficos (5%)

```
---

## 🎯 Escala de Classificação (0-10)

| Score | Classificação | Descrição | Kelly % |
|-------|--------------|-----------|---------|
| 0-2 | **Crítico** | Risco extremo, ação imediata | 0% |
| 2-4 | **Ruim** | Condições desfavoráveis | 10% |
| 4-6 | **Neutro** | Mercado equilibrado | 25% |
| 6-8 | **Bom** | Condições favoráveis | 50% |
| 8-10 | **Ótimo** | Oportunidade excepcional | 75% |

---

## 📈 1. CICLO (40% do peso total)

### MVRV Z-Score (20%)
**Fórmula**: `(Market Value - Realized Value) / Std Dev`
**Fonte**: Glassnode, CryptoQuant

| Z-Score | Score | Classificação |
|---------|-------|--------------|
| < 0 | 9-10 | Ótimo |
| 0-2 | 7-8 | Bom |
| 2-4 | 5-6 | Neutro |
| 4-6 | 3-4 | Ruim |
| > 6 | 0-2 | Crítico |

### Realized Price Ratio (15%)
**Fórmula**: `Preço BTC / Realized Price`
**Fonte**: Glassnode, LookIntoBitcoin

| Ratio | Score | Classificação |
|-------|-------|--------------|
| < 0.7 | 9-10 | Ótimo |
| 0.7-1.0 | 7-8 | Bom |
| 1.0-1.5 | 5-6 | Neutro |
| 1.5-2.5 | 3-4 | Ruim |
| > 2.5 | 0-2 | Crítico |

### Puell Multiple (5%) [NOVO]
**Fórmula**: `(Mineração Diária USD) / (MA 365 dias)`
**Fonte**: Glassnode, LookIntoBitcoin

| Multiple | Score | Classificação |
|----------|-------|--------------|
| < 0.5 | 9-10 | Ótimo |
| 0.5-1.0 | 7-8 | Bom |
| 1.0-2.0 | 5-6 | Neutro |
| 2.0-4.0 | 3-4 | Ruim |
| > 4.0 | 0-2 | Crítico |

---

## 📊 2. MOMENTUM (25% do peso total)

### RSI Semanal (10%)
**Fonte**: TradingView, Glassnode

| RSI | Score | Classificação |
|-----|-------|--------------|
| < 30 | 9-10 | Ótimo |
| 30-45 | 7-8 | Bom |
| 45-55 | 5-6 | Neutro |
| 55-70 | 3-4 | Ruim |
| > 70 | 0-2 | Crítico |

### Funding Rates - Média 7D (8%)
**Fonte**: Coinglass, Glassnode

| Funding Rate | Score | Classificação |
|--------------|-------|--------------|
| < -0.05% | 9-10 | Ótimo |
| -0.05% a 0% | 7-8 | Bom |
| 0% a 0.02% | 5-6 | Neutro |
| 0.02% a 0.1% | 3-4 | Ruim |
| > 0.1% | 0-2 | Crítico |

### Open Interest Change 30D (4%)
**Fórmula**: `(OI Atual - OI 30D atrás) / OI 30D atrás × 100`

| OI Change % | Score | Classificação |
|-------------|-------|--------------|
| < -30% | 9-10 | Ótimo |
| -30% a -10% | 7-8 | Bom |
| -10% a +20% | 5-6 | Neutro |
| +20% a +50% | 3-4 | Ruim |
| > +50% | 0-2 | Crítico |

### Long/Short Ratio (3%) [NOVO]
**Fonte**: Coinglass, Binance

| L/S Ratio | Score | Classificação |
|-----------|-------|--------------|
| < 0.8 | 9-10 | Ótimo |
| 0.8-0.95 | 7-8 | Bom |
| 0.95-1.05 | 5-6 | Neutro |
| 1.05-1.3 | 3-4 | Ruim |
| > 1.3 | 0-2 | Crítico |

---

## ⚠️ 3. RISCO (15% do peso total)

### Distância do Liquidation (6%)
**Fórmula**: `((Preço Atual - Preço Liquidação) / Preço Atual) × 100`

| Distância % | Score | Classificação |
|-------------|-------|--------------|
| > 50% | 9-10 | Ótimo |
| 30-50% | 7-8 | Bom |
| 20-30% | 5-6 | Neutro |
| 10-20% | 3-4 | Ruim |
| < 10% | 0-2 | Crítico |

### Health Factor AAVE (4%)

| Health Factor | Score | Classificação |
|---------------|-------|--------------|
| > 2.0 | 9-10 | Ótimo |
| 1.5-2.0 | 7-8 | Bom |
| 1.3-1.5 | 5-6 | Neutro |
| 1.1-1.3 | 3-4 | Ruim |
| < 1.1 | 0-2 | Crítico |

### Exchange Netflow 7D (3%)
**Fonte**: CryptoQuant, Glassnode

| Netflow | Score | Classificação |
|---------|-------|--------------|
| < -50k BTC | 9-10 | Ótimo |
| -50k a -10k | 7-8 | Bom |
| -10k a +10k | 5-6 | Neutro |
| +10k a +50k | 3-4 | Ruim |
| > +50k BTC | 0-2 | Crítico |

### Stablecoin Supply Ratio (2%) [NOVO]
**Fórmula**: `Market Cap Stablecoins / Market Cap BTC`

| SSR | Score | Classificação |
|-----|-------|--------------|
| > 15% | 9-10 | Ótimo |
| 10-15% | 7-8 | Bom |
| 5-10% | 5-6 | Neutro |
| 2-5% | 3-4 | Ruim |
| < 2% | 0-2 | Crítico |

---

## 📉 4. TÉCNICO (20% do peso total) [NOVO]

### Posição vs EMA 200 (8%)
**Timeframe**: Diário

| Distância | Score | Classificação |
|-----------|-------|--------------|
| < -20% | 9-10 | Ótimo |
| -20% a -5% | 7-8 | Bom |
| -5% a +5% | 5-6 | Neutro |
| +5% a +30% | 3-4 | Ruim |
| > +30% | 0-2 | Crítico |

### Estrutura de EMAs (7%)
**EMAs**: 21, 50, 200

| Estrutura | Score | Classificação |
|-----------|-------|--------------|
| EMA21 > EMA50 > EMA200 | 9-10 | Bull Perfeito |
| Preço > EMA200, EMAs mistas | 6-8 | Bull Inicial |
| EMAs laterais/cruzadas | 4-6 | Indefinido |
| EMA21 < EMA50 < EMA200 | 2-4 | Bear Confirmado |
| Preço < todas EMAs | 0-2 | Bear Extremo |

### Padrões Gráficos (5%)
**Análise**: Manual ou algoritmo de detecção

| Padrão | Score | Confiabilidade |
|--------|-------|----------------|
| Double Bottom / Inverse H&S | 8-10 | Alta |
| Bull Flag / Ascending Triangle | 7-8 | Média-Alta |
| Sem padrão claro | 4-6 | N/A |
| Bear Flag / Descending Triangle | 2-3 | Média-Alta |
| Head & Shoulders / Double Top | 0-2 | Alta |

---

## 🔔 Sistema de Alertas Aprimorado

### Alertas Críticos
```javascript
// Score Based
if (score < 2) alert("CRÍTICO: Zerar alavancagem imediatamente");
if (score_change_24h > 3) alert("Mudança drástica de regime");

// Risk Based
if (health_factor < 1.15) alert("PERIGO: Liquidação próxima");
if (dist_liquidation < 15) alert("ATENÇÃO: Revisar posição");

// Market Based
if (funding_rate > 0.1) alert("EUFORIA: Considerar redução");
if (mvrv_z > 6) alert("TOPO: Preparar saída gradual");

// Technical Based
if (price_crosses_ema200) alert("Mudança de tendência principal");
if (ema_death_cross) alert("Death Cross: Bear market provável");
```

### Alertas de Divergência
```javascript
// Divergência Alta-Baixa
if (price_new_high && rsi < 50) {
    alert("DIVERGÊNCIA NEGATIVA: Topo provável");
}

// Divergência Volume
if (price_up && volume_down) {
    alert("Rally sem volume: Cautela");
}

// Divergência On-Chain
if (price_up && exchange_inflow > 50k) {
    alert("Distribuição detectada");
}
```

### Alertas de Oportunidade
```javascript
// Capitulação
if (mvrv_z < 0 && funding < -0.1) {
    alert("CAPITULAÇÃO: Oportunidade histórica");
}

// Acumulação
if (exchange_outflow > 50k && rsi < 40) {
    alert("Smart money acumulando");
}
```

---

## ⚖️ Ajustes Dinâmicos de Peso

### Por Regime de Mercado
```javascript
function ajustarPesos(mvrv_z_score) {
    if (mvrv_z_score < 0) {
        // Bear Extremo
        return {
            ciclo: 0.50,      // +10%
            momentum: 0.20,   // -5%
            risco: 0.10,      // -5%
            tecnico: 0.20     // 0%
        };
    } else if (mvrv_z_score > 6) {
        // Bull Extremo
        return {
            ciclo: 0.30,      // -10%
            momentum: 0.30,   // +5%
            risco: 0.25,      // +10%
            tecnico: 0.15     // -5%
        };
    } else {
        // Neutro
        return {
            ciclo: 0.40,
            momentum: 0.25,
            risco: 0.15,
            tecnico: 0.20
        };
    }
}
```

### Por Volatilidade
```javascript
function ajustarPorVolatilidade(btc_volatility_30d) {
    if (btc_volatility_30d > 80) {
        // Alta volatilidade
        peso_risco *= 1.5;
        peso_tecnico *= 1.2;
    } else if (btc_volatility_30d < 30) {
        // Baixa volatilidade
        peso_ciclo *= 1.2;
        peso_momentum *= 0.8;
    }
}
```

---

## 📊 Score de Volatilidade (Modificador)

### Bitcoin Volatility Index (BVOL)
```javascript
function calcularModificadorVolatilidade(bvol) {
    if (bvol < 30) return 1.1;       // Baixa vol = bonus
    if (bvol < 50) return 1.0;       // Normal
    if (bvol < 80) return 0.9;       // Alta vol = penalidade
    if (bvol >= 80) return 0.8;      // Vol extrema
}

// Aplicação
score_final = score_base * modificador_volatilidade;
kelly_allocation = kelly_base * modificador_volatilidade;
```

---

## 🎯 Modelo de Alocação Core-Satellite

### Estrutura Base
```
PATRIMÔNIO TOTAL BTC
├── Core Position (50%) - HOLD PURO
│   └── Nunca alavancado
└── Satellite Position (50%) - HOLD ALAVANCADO
    └── Aplicar sistema de score
```

### Tabela de Aplicação Kelly 
| Score | Classificação | Conservador | Moderado | Agressivo | Extremo* |
|-------|--------------|-------------|----------|-----------|----------|
| 0-2   | Crítico      | 1.0x        | 1.0x     | 1.0x      | 1.0x     |
| 2-4   | Ruim         | 1.1x        | 1.2x     | 1.3x      | 1.5x     |
| 4-6   | Neutro       | 1.2x        | 1.4x     | 1.6x      | 2.0x     |
| 6-8   | Bom          | 1.35x       | 1.7x     | 2.0x      | 2.5x     |
| 8-10  | Ótimo        | 1.5x        | 2.0x     | 2.5x      | 3.0x     |

*Extremo = Apenas para traders experientes em condições excepcionais

🛡️ Fatores de Segurança por Perfil

PERFIL CONSERVADOR (Recomendado)
├── Alavancagem Máxima: 1.5x
├── Stop Loss: -10%
├── Health Factor Mínimo: 1.5
└── Experiência: Iniciante

PERFIL MODERADO
├── Alavancagem Máxima: 2.0x
├── Stop Loss: -8%
├── Health Factor Mínimo: 1.4
└── Experiência: 6+ meses

PERFIL AGRESSIVO
├── Alavancagem Máxima: 2.5x
├── Stop Loss: -6%
├── Health Factor Mínimo: 1.3
└── Experiência: 1+ ano

PERFIL EXTREMO
├── Alavancagem Máxima: 3.0x
├── Stop Loss: -5%
├── Health Factor Mínimo: 1.25
└── Experiência: 2+ anos

📊 Condições para Alavancagem 3X
TODOS os critérios devem ser atendidos:

CHECKLIST 3X (Score 8-10)
□ MVRV Z-Score < 0 (fundo histórico)
□ RSI Semanal < 30 (extremo oversold)
□ Exchange Netflow < -50k BTC (acumulação massiva)
□ Funding Rates < -0.05% (shorts pagando)
□ Preço > 20% abaixo da EMA200
□ Volume de compra > 2x média
□ Sem eventos macro negativos próximos
□ Capital que pode perder 100%

⚠️ Tabela de Risco por Alavancagem

| Alavancagem | Queda para Liquidação | Volatilidade Diária Máxima | Risco de Ruin |
|-------------|----------------------|---------------------------|---------------|
| 1.0x        | Impossível           | Ilimitada                 | 0%            |
| 1.5x        | -33%                 | 10%                       | 5%            |
| 2.0x        | -25%                 | 8%                        | 15%           |
| 2.5x        | -20%                 | 6%                        | 30%           |
| 3.0x        | -16.7%               | 5%                        | 50%           |

🎯 Estratégia de Entrada Escalonada

ENTRADA PROGRESSIVA (para alavancagens > 2x)
├── 25% da posição com 1.5x
├── 25% adicional se confirmar suporte (2.0x)
├── 25% após rompimento de resistência (2.5x)
└── 25% final apenas se todos sinais positivos (3.0x)

Nunca all-in com alavancagem máxima!

📉 Gestão de Risco Dinâmica

def calcular_alavancagem_dinamica(score, perfil, condicoes_mercado):
    # Base
    alavancagem_base = tabela_alavancagem[score][perfil]
    
    # Modificadores
    if volatilidade_btc > 80:
        alavancagem_base *= 0.7  # Reduz 30% em alta vol
    
    if tempo_em_posicao > 30_dias:
        alavancagem_base *= 0.9  # Reduz com tempo
    
    if drawdown_portfolio > 20:
        alavancagem_base *= 0.8  # Reduz após perdas
    
    # Caps
    if perfil == "extremo" and score < 9:
        alavancagem_base = min(alavancagem_base, 2.5)
    
    return min(alavancagem_base, limite_plataforma)

🚨 Sistema de Circuit Breakers para Alta Alavancagem

TRIGGERS AUTOMÁTICOS (Alavancagem > 2x)
├── Queda 5% em 1h → Reduzir para 1.5x
├── Queda 10% em 4h → Reduzir para 1.0x
├── Volatilidade > 100% anual → Máximo 2.0x
├── Funding > 0.1% → Máximo 1.5x
└── Qualquer notícia negativa major → Fechar 50%

💰 Expectativa de Retorno vs Risco

| Alavancagem | Bull Case (+50%) | Base Case (+20%) | Bear Case (-20%) | Crash (-40%) |
|-------------|------------------|------------------|------------------|--------------|
| 1.0x        | +50%             | +20%             | -20%             | -40%         |
| 1.5x        | +75%             | +30%             | -30%             | -60%         |
| 2.0x        | +100%            | +40%             | -40%             | LIQUIDADO    |
| 2.5x        | +125%            | +50%             | LIQUIDADO        | LIQUIDADO    |
| 3.0x        | +150%            | +60%             | LIQUIDADO        | LIQUIDADO    |

🔄 Rebalanceamento por Score

REGRAS DE AJUSTE
├── Score sobe 2+ pontos → Pode aumentar 0.5x
├── Score cai 2+ pontos → Deve reduzir 0.5x
├── Score < 4 → Máximo 1.5x independente do perfil
└── Revisar alavancagem 2x ao dia

📊 Exemplo Prático - Cenário Ótimo (Score 9)

SETUP BULL MARKET BOTTOM
├── Capital: $100k
├── Score: 9/10
├── Perfil: Agressivo
├── Alavancagem Escolhida: 2.5x

EXECUÇÃO:
1. Compra $40k spot (base)
2. Espera confirmação → +$40k (1.8x)
3. Rompimento confirmado → +$20k (2.5x total)

GESTÃO:
- Stop loss: -6% do entry médio
- Take profit 1: +15% (fechar 0.5x)
- Take profit 2: +30% (fechar 1.0x)
- Let ride: 1.0x para o moon

⚡ Quick Decision Matrix

Score < 6 → Máximo 1.5x sempre
Score 6-8 + Conservador → 1.35x
Score 6-8 + Moderado → 1.7x
Score 6-8 + Agressivo → 2.0x
Score 8+ + Todos sinais OK → Até 3.0x
Qualquer dúvida → Use menos alavancagem

🎯 Regra de Ouro

"A alavancagem ideal é aquela que te deixa dormir tranquilo. Se está perdendo sono, reduza pela metade."
---


## 📋 Padrão de Saída JSON

```json
{
  "timestamp": "2025-05-25T14:30:00Z",
  "score_final": 5.85,
  "score_ajustado": 5.27,
  "modificador_volatilidade": 0.9,
  "classificacao_geral": "Neutro",
  "kelly_allocation": "25%",
  "acao_recomendada": "Manter posição conservadora",
  "alertas_ativos": [
    "Volatilidade elevada",
    "EMA200 como resistência"
  ],
  "pesos_dinamicos": {
    "ciclo": 0.40,
    "momentum": 0.25,
    "risco": 0.15,
    "tecnico": 0.20
  },
  "blocos": {
    "ciclo": {
      "peso": "40%",
      "score": 2.34,
      "indicadores": {
        "MVRV_Z": { "valor": 2.1, "score": 6.0 },
        "Realized_Ratio": { "valor": 1.3, "score": 5.5 },
        "Puell_Multiple": { "valor": 1.2, "score": 5.0 }
      }
    },
    "momentum": {
      "peso": "25%",
      "score": 1.46,
      "indicadores": {
        "RSI_Semanal": { "valor": 52, "score": 5.5 },
        "Funding_Rates": { "valor": "0.015%", "score": 5.5 },
        "OI_Change": { "valor": "+12%", "score": 5.5 },
        "Long_Short_Ratio": { "valor": 0.98, "score": 6.0 }
      }
    },
    "risco": {
      "peso": "15%",
      "score": 0.93,
      "indicadores": {
        "Dist_Liquidacao": { "valor": "35%", "score": 7.0 },
        "Health_Factor": { "valor": 1.7, "score": 7.5 },
        "Exchange_Netflow": { "valor": "-5k", "score": 6.0 },
        "Stablecoin_Ratio": { "valor": "8%", "score": 6.0 }
      }
    },
    "tecnico": {
      "peso": "20%",
      "score": 1.12,
      "indicadores": {
        "Posicao_EMA200": { "valor": "+3%", "score": 5.5 },
        "Estrutura_EMAs": { "valor": "Mista", "score": 6.0 },
        "Padrao_Grafico": { "valor": "Consolidação", "score": 5.0 }
      }
    }
  }
}
```

---

## 🚨 Circuit Breakers

### Triggers Automáticos
| Condição | Ação | Prioridade |
|----------|------|------------|
| Score < 2 por 24h | Zerar alavancagem | CRÍTICA |
| HF < 1.2 | Deleveraging 50% | URGENTE |
| Queda > 15% em 4h | Pausar sistema 24h | ALTA |
| Funding > 0.3% por 3 dias | Máximo 25% alavancagem | MÉDIA |
| Score muda > 3 pontos em 24h | Revisão manual obrigatória | ALTA |

---

## 📝 Notas de Implementação

1. **Frequência de Cálculo**: 
   - Completo: 2x ao dia (00h e 12h UTC)
   - Health Factor: A cada hora
   - Alertas críticos: Real-time

2. **Prioridade de Dados**:
   - Tier 1: MVRV, EMA200, Health Factor
   - Tier 2: RSI, Funding, Exchange Flow
   - Tier 3: Padrões, Puell, Stablecoin

3. **Fallback**:
   - Se indicador indisponível, usar peso 0
   - Recalcular proporcionalmente outros

---

*Versão 2.0 - Atualizada em 25/05/2025 - 22:55