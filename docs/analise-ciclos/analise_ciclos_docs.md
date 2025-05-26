# 📈 Análise de Ciclos do BTC

**Endpoint:** `/api/v1/analise-ciclos`  
**Versão:** v1.0 (Atualizada - Maio 2025)  
**Método:** GET

## 🎯 Objetivo

Determinar de forma quantitativa se o mercado do Bitcoin está em Bull Market ou Bear Market, avaliando também a força do ciclo através de 5 indicadores fundamentais com score ponderado de 0 a 10.

---

## 📊 Estrutura de Resposta

```json
{
    "categoria": "Análise de Ciclos do BTC",
    "score_consolidado": 7.85,
    "classificacao": "Bull Moderado",
    "observacao": "Score consolidado 7.85. Destaques: BTC_EMA: forte (8.5), Realized: moderado (7.2), Puell: forte (9.1)",
    "resumo_executivo": {
        "estrategia_recomendada": "Operações com Cautela",
        "exposicao_sugerida": "Alavancagem moderada (2-3x máximo)",
        "gestao_risco": "Monitoramento constante de riscos, stop loss apertado",
        "outlook": "Ambiente favorável mas com necessidade de cautela devido a alguns indicadores neutros"
    },
    "indicadores": [...]
}
```

### **Score e Classificação Final**

| Score Range | Classificação | Descrição |
|-------------|---------------|-----------|
| **8.1 - 10.0** | **Bull Forte** | Condições ideais para operações alavancadas |
| **6.1 - 8.0** | **Bull Moderado** | Condições favoráveis com cautela |
| **4.1 - 6.0** | **Tendência Neutra** | Mercado indefinido, evitar alavancagem |
| **2.1 - 4.0** | **Bear Leve** | Condições desfavoráveis |
| **0.0 - 2.0** | **Bear Forte** | Evitar operações de alta |

---

## 🧮 Indicadores e Pesos

### **1. BTC vs EMA 200D** (Peso: 30%)

**Objetivo:** Medir a força do bull market baseado na distância do preço atual vs EMA 200 dias.

**Fórmula:** `((Preço_Atual - EMA_200) / EMA_200) × 100`

| Variação % | Classificação | Score |
|------------|---------------|-------|
| > +30% | Bull Parabólico | **10.0** |
| +15% a +30% | Bull Forte | **8.0** |
| +5% a +15% | Bull Moderado | **6.0** |
| 0% a +5% | Bull Inicial | **4.0** |
| < 0% | Bull Não Confirmado | **2.0** |

**Formato de Saída:**
```json
{
    "indicador": "BTC vs EMA 200D",
    "fonte": "TradingView",
    "valor_coletado": "BTC +18.5% vs EMA 200D",
    "score": 8.0,
    "score_ponderado (8.0 × 0.30)": 2.4,
    "classificacao": "Bull Forte",
    "observacao": "Força do bull market baseada na distância do preço atual vs EMA 200 dias",
    "detalhes": {
        "dados_coletados": {
            "preco_atual": 67500.00,
            "ema_200": 57000.00,
            "fonte": "TradingView/Binance"
        },
        "calculo": {
            "formula": "((67500 - 57000) / 57000) × 100",
            "variacao_percentual": 18.42,
            "faixa_classificacao": "+15% a +30%"
        },
        "racional": "Preço 18.42% acima da EMA 200D indica bull market forte com tendência bem estabelecida"
    }
}
```

---

### **2. BTC vs Realized Price** (Peso: 30%)

**Objetivo:** Avaliar a fase do ciclo comparando preço de mercado com preço médio pago pelos holders.

**Fórmula:** `((Preço_Atual - Realized_Price) / Realized_Price) × 100`

| Variação % | Classificação | Score |
|------------|---------------|-------|
| > +50% | Ciclo Aquecido | **10.0** |
| +20% a +50% | Ciclo Normal | **8.0** |
| -10% a +20% | Acumulação | **6.0** |
| -30% a -10% | Capitulação Leve | **4.0** |
| < -30% | Capitulação Severa | **2.0** |

**Formato de Saída:**
```json
{
    "indicador": "BTC vs Realized Price",
    "fonte": "Glassnode via APIs",
    "valor_coletado": "BTC +35.2% vs Realized Price",
    "score": 8.0,
    "score_ponderado (8.0 × 0.30)": 2.4,
    "classificacao": "Ciclo Normal",
    "observacao": "Compara preço de mercado com preço médio pago pelos holders para avaliar fase do ciclo",
    "detalhes": {
        "dados_coletados": {
            "preco_atual": 67500.00,
            "realized_price": 49900.00,
            "fonte": "Glassnode/APIs"
        },
        "calculo": {
            "formula": "((67500 - 49900) / 49900) × 100",
            "variacao_percentual": 35.27,
            "faixa_classificacao": "+20% a +50%"
        },
        "racional": "Preço 35% acima do Realized Price indica ciclo normal com holders em lucro moderado"
    }
}
```

---

### **3. Puell Multiple** (Peso: 20%)

**Objetivo:** Analisar pressão dos mineradores através da receita diária vs média de 1 ano.

**Fórmula:** `Receita_Diária_Mineradores / Média_365_Dias`

| Valor | Classificação | Score |
|-------|---------------|-------|
| 0.5 - 1.2 | Zona Ideal | **10.0** |
| 1.2 - 1.8 | Leve Aquecimento | **8.0** |
| 0.3 - 0.5 ou 1.8 - 2.5 | Neutro | **6.0** |
| 2.5 - 4.0 | Tensão Alta | **4.0** |
| < 0.3 ou > 4.0 | Extremo | **2.0** |

**Formato de Saída:**
```json
{
    "indicador": "Puell Multiple",
    "fonte": "Glassnode via APIs",
    "valor_coletado": "0.95",
    "score": 10.0,
    "score_ponderado (10.0 × 0.20)": 2.0,
    "classificacao": "Zona Ideal",
    "observacao": "Ratio da receita diária dos mineradores vs média de 1 ano - indica pressão de venda",
    "detalhes": {
        "dados_coletados": {
            "puell_value": 0.95,
            "receita_diaria": 45000000,
            "media_365d": 47368421,
            "fonte": "Glassnode/APIs"
        },
        "calculo": {
            "formula": "Receita_Diária / Média_365_Dias",
            "resultado": 0.95,
            "faixa_classificacao": "0.5 - 1.2"
        },
        "racional": "Puell de 0.95 indica receita dos mineradores dentro da zona ideal, pressão de venda baixa"
    }
}
```

---

### **4. M2 Global Momentum** (Peso: 15%)

**Objetivo:** Avaliar velocidade de mudança na expansão monetária global.

**Fórmula:** `Taxa_Crescimento_M2_Trimestral_Anualizada`

| Momentum % | Classificação | Score |
|------------|---------------|-------|
| > +3% | Aceleração Forte | **10.0** |
| +1% a +3% | Aceleração Moderada | **8.0** |
| -1% a +1% | Estável | **6.0** |
| -3% a -1% | Desaceleração | **4.0** |
| < -3% | Contração | **2.0** |

**Formato de Saída:**
```json
{
    "indicador": "M2 Global Momentum",
    "fonte": "TradingView APIs",
    "valor_coletado": "+2.3% momentum",
    "score": 8.0,
    "score_ponderado (8.0 × 0.15)": 1.2,
    "classificacao": "Aceleração Moderada",
    "observacao": "Velocidade de mudança na expansão monetária global - indica aceleração ou desaceleração de liquidez",
    "detalhes": {
        "dados_coletados": {
            "momentum_value": 2.3,
            "m2_atual": 21500000000000,
            "m2_trimestre_anterior": 21000000000000,
            "fonte": "TradingView/Fed/BCE"
        },
        "calculo": {
            "formula": "((M2_Atual - M2_Anterior) / M2_Anterior) × 100 × 4",
            "variacao_trimestral": 2.38,
            "momentum_anualizado": 2.3,
            "faixa_classificacao": "+1% a +3%"
        },
        "racional": "Momentum de +2.3% indica aceleração moderada de liquidez global, favorável para ativos de risco"
    }
}
```

---

### **5. Funding Rates 7D** (Peso: 5%)

**Objetivo:** Avaliar sentimento do mercado através das taxas de financiamento dos contratos perpétuos.

**Fórmula:** `Média_7_Dias_Funding_Rates × 100`

| Taxa % | Classificação | Score |
|--------|---------------|-------|
| 0% - 0.1% | Sentimento Equilibrado | **10.0** |
| 0.1% - 0.2% | Otimismo Moderado | **8.0** |
| 0.2% - 0.3% | Aquecimento | **6.0** |
| 0.3% - 0.5% | Euforia Inicial | **4.0** |
| > 0.5% | Euforia Extrema | **2.0** |

**Formato de Saída:**
```json
{
    "indicador": "Funding Rates 7D Média",
    "fonte": "Binance API",
    "valor_coletado": "0.085%",
    "score": 10.0,
    "score_ponderado (10.0 × 0.05)": 0.5,
    "classificacao": "Sentimento Equilibrado",
    "observacao": "Média de 7 dias das taxas de funding dos contratos perpétuos - indica sentimento do mercado",
    "detalhes": {
        "dados_coletados": {
            "funding_rate_7d": 0.085,
            "total_coletas": 56,
            "exchange": "Binance",
            "simbolo": "BTCUSDT"
        },
        "calculo": {
            "formula": "Soma(Funding_Rates_7D) / 56",
            "taxa_media": 0.085,
            "faixa_classificacao": "0% - 0.1%"
        },
        "racional": "Funding rate de 0.085% indica sentimento equilibrado sem excessos de otimismo ou pessimismo"
    }
}
```

---

## 🔧 Especificações Técnicas

### **Parâmetros de Entrada**
```
GET /api/v1/analise-ciclos
```
*Não requer parâmetros - credenciais TradingView configuradas via variáveis de ambiente*

### **Headers Requeridos**
```
Content-Type: application/json
```

### **Códigos de Resposta**
- **200 OK**: Análise realizada com sucesso
- **400 Bad Request**: Parâmetros inválidos
- **500 Internal Server Error**: Erro na coleta de dados
- **503 Service Unavailable**: APIs externas indisponíveis

### **Tratamento de Erros**
Em caso de falha na coleta de dados específicos:
- **Score = 0.0** (valor padrão para indicador com erro)
- Campo `observacao` indica descrição detalhada do erro
- Campo `score_ponderado` = 0.0 (não contribui para score final)
- API continua funcionando com dados disponíveis dos outros indicadores

**Exemplo de indicador com erro:**
```json
{
    "indicador": "BTC vs Realized Price",
    "fonte": "Glassnode via APIs",
    "valor_coletado": "erro",
    "score": 0.0,
    "score_ponderado (0.0 × 0.30)": 0.0,
    "classificacao": "Dados indisponíveis",
    "observacao": "Erro ao conectar com API Glassnode: timeout após 10s. Verifique conexão ou status da API externa."
}
```

---

## 📈 Interpretação dos Resultados

### **Score Consolidado: Cálculo**
```
Score_Final = (BTC_EMA × 0.30) + (Realized × 0.30) + (Puell × 0.20) + (M2 × 0.15) + (Funding × 0.05)
```

### **Estratégias por Classificação**

**Bull Forte (8.1-10.0):**
```json
"resumo_executivo": {
    "estrategia_recomendada": "Operações Agressivas",
    "exposicao_sugerida": "Alavancagem alta (3-5x), exposição máxima ao BTC",
    "gestao_risco": "Stop loss moderado, trailing stops para capturar tendência",
    "outlook": "Ambiente ideal para hold alavancado - todos os indicadores favoráveis"
}
```

**Bull Moderado (6.1-8.0):**
```json
"resumo_executivo": {
    "estrategia_recomendada": "Operações com Cautela",
    "exposicao_sugerida": "Alavancagem moderada (2-3x máximo)",
    "gestao_risco": "Monitoramento constante, stop loss apertado",
    "outlook": "Ambiente favorável mas com necessidade de cautela"
}
```

**Tendência Neutra (4.1-6.0):**
```json
"resumo_executivo": {
    "estrategia_recomendada": "Aguardar Definição",
    "exposicao_sugerida": "Evitar alavancagem, posições pequenas se houver",
    "gestao_risco": "Preservação de capital como prioridade máxima",
    "outlook": "Mercado indefinido - aguardar sinais mais claros"
}
```

**Bear Leve (2.1-4.0):**
```json
"resumo_executivo": {
    "estrategia_recomendada": "Posições Defensivas",
    "exposicao_sugerida": "Reduzir exposição, considerar hedge parcial",
    "gestao_risco": "Stop loss muito apertado, gestão rigorosa",
    "outlook": "Condições desfavoráveis - foco em proteção"
}
```

**Bear Forte (0.0-2.0):**
```json
"resumo_executivo": {
    "estrategia_recomendada": "Evitar Operações de Alta",
    "exposicao_sugerida": "Cash ou hedge completo, aguardar reversão",
    "gestao_risco": "Não operar alta - risco muito elevado",
    "outlook": "Ciclo de baixa confirmado - aguardar fundo"
}
```

---

## 📚 Referências Técnicas

### **Fontes de Dados**
- **TradingView:** BTC/USD preços e EMAs *(credenciais via variáveis de ambiente)*
- **Binance API:** Funding rates *(acesso público)*
- **Glassnode APIs:** Realized Price, Puell Multiple *(chaves via ambiente)*
- **Fed/BCE APIs:** M2 Global data *(acesso público)*
- **Notion (fallback):** Dados de backup *(token via ambiente)*

**Variáveis de Ambiente Requeridas:**
```bash
TV_USERNAME=seu_usuario_tradingview
TV_PASSWORD=sua_senha_tradingview
GLASSNODE_API_KEY=sua_chave_glassnode
NOTION_TOKEN=seu_token_notion
NOTION_DATABASE_ID_MACRO=id_do_database_macro
```

### **Atualizações**
- **Frequência:** Dados atualizados a cada requisição
- **Cache:** Sem cache local (sempre dados atuais)
- **Latência:** ~2-5 segundos por análise completa

---

## ⚠️ Observações Importantes

1. **Esta análise é uma ferramenta de apoio**, não constitui recomendação de investimento
2. **Mercados financeiros envolvem riscos** - use sempre gestão de risco adequada
3. **Dados históricos não garantem resultados futuros**
4. **Combine com outras análises** técnicas e fundamentais
5. **Score máximo teórico: 10.0** - todos os indicadores na classificação máxima

---

**Última Atualização:** 23 de Maio de 2025  
**Versão da API:** v1.0  
**Status:** Produção (Railway)