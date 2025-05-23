# 🎯 Análise de Ciclos BTC - v2.0

---

## 🎯 Objetivo

Confirmar de forma **objetiva e quantitativa** se o mercado do Bitcoin está em **Bull Market** ou **Bear Market**, avaliando também a **força do ciclo**.

---

## 🧩 Indicadores Utilizados e Pesos

| Indicador | Peso (%) | Fonte de Dados |
| --- | --- | --- |
| **BTC preço vs EMA 200D** | **30%** | TradingView |
| **BTC preço vs Realized Price** | **30%** | Notion API / Glassnode |
| **Puell Multiple** | **20%** | Notion API / Glassnode |
| **M2 Global Momentum** | **15%** | TradingView APIs (4 economias) |
| **Funding Rates 7D Média** | **5%** | Binance API |

---

## 📊 Escala de Avaliação (0-10)

### **🔵 BTC vs EMA 200D - Força do Bull Market**
| Variação vs EMA 200D | Score | Classificação |
| --- | --- | --- |
| > +30% | 9.0 | Bull Parabólico |
| +15% a +30% | 7.0 | Bull Forte |
| +5% a +15% | 5.0 | Bull Moderado |
| 0% a +5% | 3.0 | Bull Inicial |
| < 0% | 1.0 | Bull Não Confirmado |

### **💰 BTC vs Realized Price - Fase do Ciclo**
| Variação vs Realized Price | Score | Classificação |
| --- | --- | --- |
| > +50% | 9.0 | Ciclo Aquecido |
| +20% a +50% | 7.0 | Ciclo Normal |
| -10% a +20% | 5.0 | Acumulação |
| -30% a -10% | 3.0 | Capitulação Leve |
| < -30% | 1.0 | Capitulação Severa |

### **⚖️ Puell Multiple - Pressão dos Mineradores**
| Valor Puell Multiple | Score | Classificação |
| --- | --- | --- |
| 0.5 - 1.2 | 9.0 | Zona Ideal |
| 1.2 - 1.8 | 7.0 | Leve Aquecimento |
| 0.3 - 0.5 ou 1.8 - 2.5 | 5.0 | Neutro |
| 2.5 - 4.0 | 3.0 | Tensão Alta |
| Fora das faixas | 1.0 | Extremo |

### **🌍 M2 Global Momentum - Liquidez Global**
| Vigor M2 (YoY + 5×diferença) | Score | Classificação |
| --- | --- | --- |
| > 3% | 9.0 | Aceleração Forte |
| 1% a 3% | 7.0 | Aceleração Moderada |
| -1% a 1% | 5.0 | Estável |
| -3% a -1% | 3.0 | Desaceleração |
| < -3% | 1.0 | Contração |

### **📈 Funding Rates 7D - Sentimento do Mercado**
| Taxa Funding Média | Score | Classificação |
| --- | --- | --- |
| 0% - 0.1% | 9.0 | Sentimento Equilibrado |
| 0.1% - 0.2% | 7.0 | Otimismo Moderado |
| 0.2% - 0.3% | 5.0 | Aquecimento |
| 0.3% - 0.5% | 3.0 | Euforia Inicial |
| > 0.5% | 1.0 | Euforia Extrema |

---

## 🧮 Cálculo do Score Consolidado

**Fórmula:**
```
Score Final = (BTC vs EMA × 0.30) + (BTC vs Realized × 0.30) + 
              (Puell Multiple × 0.20) + (M2 Global × 0.15) + 
              (Funding Rates × 0.05)
```

**Pontuação Máxima:** 9.0 (quando todos indicadores = 9.0)

---

## 📊 Classificação Final (5 Níveis)

| Score Consolidado | Interpretação | Estratégia |
| --- | --- | --- |
| **8.1–10.0** | 🟢 **Bull Forte** | Operar agressivamente |
| **6.1–8.0** | 🔵 **Bull Moderado** | Operar com tamanho controlado |
| **4.1–6.0** | 🟡 **Tendência Neutra** | Analisar com cautela, pouca exposição |
| **2.1–4.0** | 🟠 **Bear Leve** | Atenção / Exposição mínima |
| **0.0–2.0** | 🔴 **Bear Forte** | Defesa máxima (nada de novas operações) |

---

## 📋 Formato de Saída JSON

```json
{
  "categoria": "Análise de Ciclos do BTC",
  "score_consolidado": 7.2,
  "classificacao": "🔵 Bull Moderado",
  "Observação": "Score consolidado 7.2. Destaques: BTC: forte (8.5), M2: forte (9.0)",
  "indicadores": [
    {
      "indicador": "BTC vs EMA 200D",
      "fonte": "TradingView",
      "valor_coletado": "BTC 18.5% vs EMA 200D",
      "score": 7.0,
      "score_ponderado (score × peso)": 2.1,
      "classificacao": "Bull Forte",
      "observação": "Força do bull market baseada na distância do preço atual vs EMA 200 dias"
    }
  ]
}
```

---

## 🔄 Principais Mudanças da v2.0

### **Indicadores Removidos:**
- ❌ BTC Dominance Tendência (20%)
- ❌ Macro Ambiente Juros (10%)

### **Indicadores Adicionados:**
- ✅ **M2 Global Momentum (15%)**: Liquidez global real (EUA+China+Eurozona+Japão)
- ✅ **Funding Rates 7D (5%)**: Sentimento do mercado de futuros

### **Indicadores Atualizados:**
- 🔄 **BTC vs EMA 200D**: Sistema 0-10 com foco na força do bull market
- 🔄 **Pesos rebalanceados**: EMA e Realized Price ganharam importância (30% cada)

---

## 🕒 Frequência de Atualização

- **Tempo real** via API
- **M2 Global**: Atualizado mensalmente (dados econômicos)
- **Demais indicadores**: Atualização diária

---

## 📡 Endpoint API

```
GET /api/v1/analise-ciclos
```

**Resposta:** Score consolidado + análise detalhada de cada indicador