# Análise de Risco

## 🎯 Objetivo

Avaliar, pontuar e consolidar o risco da operação de hold alavancado de Bitcoin, utilizando uma metodologia modular, ponderada e crítica, focada na preservação de patrimônio e controle de riscos sistêmicos.

---

## 📥 1. Entrada de Dados Obrigatórios

- Status das EMAs por timeframe (1W, 1D, 4H, 1H, 30M, 15M)
- IFR >70 por timeframe (1W, 1D, 4H, 1H, 30M, 15M)
- Divergência IFR por timeframe (1W, 1D, 4H, 1H, 30M, 15M)
- Fundamentos BTC (Model Variance, MVRV, VDD)
- Fear & Greed Index
- Indicadores Macroeconômicos (MOVE, DXY, VIX, US10Y, Ouro, M2)
- Health Factor (atual)
- Alavancagem Real
- Eventos Críticos de Plataforma (AAVE, ETH, USDC)
- WBTC Supply (anormalidades)
- WBTC Paridade BTC

---

## ⚙️ 2. Estrutura de Avaliação Interna

### 2.1 Risco Técnico

| Fator | Semanal (1W) | Diário (1D) | 4H | Intradays (1H/30M/15M) |
| --- | --- | --- | --- | --- |
| EMAs (Fraqueza) | +2.0 | +1.5 | +1.0 | +0.5 |
| IFR >70 | +2.0 | +1.5 | +1.0 | +0.5 |
| Divergência IFR | +2.0 | +1.5 | +1.0 | +0.5 |

---

### 2.2 Risco Estrutural BTC

| Fator | Peso Máximo |
| --- | --- |
| Fundamentos BTC (Model Variance, MVRV, VDD) | +3 |
| Fear & Greed Index (Escala progressiva 80–100) | até +3 |

---

### 2.3 Risco Macroeconômico e Plataforma

| Fator | Peso Máximo |
| --- | --- |
| Indicadores Macroeconômicos (MOVE, DXY, VIX, US10Y, Ouro, M2 Global) | +6 |
| Eventos Críticos de Plataforma | +5 |

---

### 2.4 Risco Financeiro Direto

| Fator | Peso Máximo |
| --- | --- |
| Health Factor (linear conforme nível) | até +7 |
| Alavancagem Real (linear conforme nível) | até +4 |
| WBTC Supply Anormal | +3 |
| WBTC Paridade BTC (Escala progressiva por % descolamento) | até +7 |

---

## 📋 3. Escalas Especiais

### 3.1 Health Factor

| HF Atual | Pontuação |
| --- | --- |
| <1.10 | +7 |
| 1.10–1.15 | +5 |
| 1.15–1.30 | +3 |
| 1.30–1.50 | +2 |
| >1.50 | 0 |

---

### 3.2 Alavancagem Real

| Alavancagem | Pontuação |
| --- | --- |
| 1X–1.5X | +1 |
| 1.5X–2X | +2 |
| 2X–3X | +4 |
| >3X | +5  |

---

### 3.3 WBTC Paridade BTC

| Spread (%) | Pontuação |
| --- | --- |
| ≤0.5% | 0 |
| 0.5%–1.0% | +1 |
| 1.0%–2.0% | +2 |
| 2.0%–5.0% | +3 |
| >5.0% | +7 |

---

### 3.4 Fear & Greed Index

| Valor | Pontuação |
| --- | --- |
| 80–85 | +1 |
| 85–90 | +1.5 |
| 90–95 | +2 |
| 95–100 | +3 |

---

## 📈 4. Como calcular o Risco Consolidado

### 4.1 execução Passo a Passo:

1. **Calcular a pontuação bruta** de cada bloco separadamente.
2. **Aplicar o peso estratégico** para cada bloco.
3. **Somar os resultados ponderados**.
4. **Normalizar a pontuação final** para a escala 0–10.

### 4.2. Ponderação Estratégica (Fórmula)

Pontuação Consolidada =
(Risco Técnico × 0.15) +
(Risco Estrutural BTC × 0.20) +
(Risco Macro/Plataforma × 0.30) +
(Risco Financeiro Direto × 0.35)

### 4.3 Pontuação Máxima Consolidada

- A pontuação máxima possível  é **14.1**.
    - 15 pontos de Risco Técnico × 0.15 ➔ 2.25
    - 6 pontos de Estrutural BTC × 0.20 ➔ 1.2
    - 11 pontos de Macro/Plataforma × 0.30 ➔ 3.3
    - 21 pontos de Financeiro Direto × 0.35 ➔ 7.35

**Total = 14.1 pontos**

### 4.4. Como normalizar a Pontuação Final para 0–10

Após consolidar, usar:

Pontuação Final Normalizada = (Pontuação Consolidada / 14.1) × 10

## 5 Tabela de Classificação do Risco

| Pontuação Final | Classificação de Risco |
| --- | --- |
| 0–2 | Risco Muito Baixo ✅ |
| 2–4 | Risco Controlado ✅ |
| 4–6 | Risco Elevado ⚠️ |
| 6–8 | Risco Crítico 🚨 |
| 8–10 | Risco Extremo 🛑 |

## 📈 6. Exemplo Prático do Cálculo

**Suponha:**

| Bloco | Pontuação Bruta |
| --- | --- |
| Risco Técnico | 4.5 pontos |
| Risco Estrutural BTC | 0.0 pontos |
| Risco Macro/Plataforma | 1.0 ponto |
| Risco Financeiro Direto | 10.0 pontos |

Aplicando a ponderação:

Pontuação Consolidada =
(4.5 × 0.15) + (0.0 × 0.20) + (1.0 × 0.30) + (10.0 × 0.35)
= 0.675 + 0 + 0.3 + 3.5
= 4.475

Normalizando:

Pontuação Final Normalizada =
(4.475 / 14.1) × 10
≈ 3.17

### Resultado Final do exemplo

| Resultado | Valor |
| --- | --- |
| Pontuação Consolidada | 4.475 |
| Pontuação Final Normalizada | 3.17 / 10 |
| Classificação de Risco | Risco Controlado ✅ |

### Entrega Final - exemplo

| Categoria do Risco | Pontuação | Alertas |
| --- | --- | --- |
| Risco Técnico | 4.5 | Falta alinhamento EMAs 4H e Intradays, Divergência IFR no 4H |
| Risco Estrutural BTC | 0.0 | Fundamentos normais, Fear & Greed neutro |
| Risco Macro e Plataforma | 1.0 | Ouro em alta forte |
| Risco Financeiro Direto | 10.0 | HF 1.13 (crítico), Alavancagem 3.2x (elevada) |

---

### Consolidação Final - exemplo

- **Pontuação Consolidada:** 4.475
- **Pontuação Final Normalizada:** (4.475 / 14.1) × 10 ≈ **3.17 / 10**
- **Classificação:** Risco Controlado ✅

---

### 📢 Observação Estratégica - exemplo

- Principais riscos: Financeiro Direto (HF e Alavancagem) e sinais técnicos moderados.
- Fundamentos e macroeconomia neutros/marginalmente pressionados.

## 7. Padrão de Entrega

### 7.1 Entrega Final - Pontuação Consolidada de Risco BTC

| Categoria do Risco | Pontuação | Alertas |
| --- | --- | --- |
| Risco Técnico | X.X | [Descrição resumida dos eventos técnicos detectados] |
| Risco Estrutural BTC | X.X | [Fundamentos esticados, Fear & Greed extremo, etc.] |
| Risco Macro e Plataforma | X.X | [MOVE alto, VIX > 25, Ouro em alta, evento de plataforma, etc.] |
| Risco Financeiro Direto | X.X | [HF abaixo de 1.15, Alavancagem acima de 3x, Supply WBTC anormal, Paridade WBTC descolada] |

---

### 7.2 Resumo gerencial do risco

- **Pontuação Final Normalizada:** X.X / 10
- **Classificação:** [Risco Muito Baixo / Controlado / Elevado / Crítico / Extremo]

---

### 7.3 Observação Estratégica

- Destacar os principais blocos de risco ativos.
- Orientar sobre o nível de atenção ou ação necessária.