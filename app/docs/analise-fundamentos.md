# Análise Fundamentalista BTC

## 🎯 Objetivo

Avaliar a **força da tendência de alta** do Bitcoin com base em fundamentos quantitativos e objetivos.

---

## 🧩 Indicadores Avaliados e Pesos

| Indicador | Peso (%) | Fonte de Dados |
| --- | --- | --- |
| **Model Variance (S2F)** | 35% | Bitcoin Magazine Pro |
| **MVRV Z-Score** | 25% | Bitcoin Magazine Pro |
| **VDD Multiple** | 20% | Bitcoin Magazine Pro |
| **M2 Global** | 20% | Bitcoin Counterflow |

---

## 📝 Template de Entrada (Coleta de Dados)

| Indicador | Valor Atual | Escala de Avaliação | Pontuação Bruta | Peso (%) | Pontuação Ponderada |
| --- | --- | --- | --- | --- | --- |
| Model Variance (S2F) | (ex: -1.2) | ≤-1.4 = +3-1.4 a -0.8 = +2-0.8 a -0.3 = +1-0.3 a 0.3 = 0 |  | 35% |  |
| MVRV Z-Score | (ex: 1.8) | <2.0 = +22.0-2.5 = +1.52.5-5.0 = +1 |  | 25% |  |
| VDD Multiple | (ex: 0.8) | <1.0 = +21.0-2.0 = +1>2.0 = 0 |  | 20% |  |
| M2 Global | (ex: Expansão 3.2%) | >3% expansão em 6M = +21-3% expansão = +1-1% a +1% = 0 |  | 20% |  |

---

## 📐 Racional de Cálculo

### 1. Para cada indicador:

Pontuação Ponderada = (Pontuação Bruta / 3) × Peso

> (dividimos por 3 porque o maior valor possível de Pontuação Bruta é 3 para o S2F, mantendo a proporcionalidade)
> 

### 2. Soma de todas as Pontuações Ponderadas.

### 3. Normalização:

Pontuação Final = (Pontuação Ponderada Total / 2.0) × 10
**Onde 2.0 é o total máximo ponderado possível.**

---

## 📊 Faixas de Interpretação (5 Escalas)

| Pontuação Final | Interpretação | Estratégia |
| --- | --- | --- |
| 0.0–2.0 | 🔴 Tendência Fundamentalista Muito Fraca | Não operar / Modo Defesa Total |
| 2.1–4.0 | 🟠 Tendência Fraca | Atenção / Operar apenas com setups muito seguros |
| 4.1–6.0 | 🟡 Tendência Moderada | Operar com cautela e risco controlado |
| 6.1–8.0 | 🔵 Tendência Forte | Operar normalmente, seguindo modelo de risco |
| 8.1–10.0 | 🟢 Tendência Muito Forte | Operar agressivamente (com gerenciamento de risco ativo) |

---

## 📎 Fontes Oficiais de Dados

| Indicador | Fonte |
| --- | --- |
| Model Variance (S2F) | [Bitcoin Magazine Pro - Stock-to-Flow Model](https://www.bitcoinmagazinepro.com/charts/stock-to-flow-model/) |
| MVRV Z-Score | [Bitcoin Magazine Pro - MVRV Z-Score](https://www.bitcoinmagazinepro.com/charts/mvrv-zscore/) |
| VDD Multiple | [Bitcoin Magazine Pro - Value Days Destroyed](https://www.bitcoinmagazinepro.com/charts/value-days-destroyed-multiple/) |
| M2 Global | [Bitcoin Counterflow - M2 Global Chart](https://bitcoincounterflow.com/charts/m2-global/) |

---

## 📋 Padrão de Entrega Executiva

### 1. Tabela Final Preenchida

| Indicador | Valor Atual | Pontuação Bruta | Peso (%) | Pontuação Ponderada |
| --- | --- | --- | --- | --- |
| Model Variance (S2F) |  |  | 35% |  |
| MVRV Z-Score |  |  | 25% |  |
| VDD Multiple |  |  | 20% |  |
| M2 Global |  |  | 20% |  |

---

### 2. Resultado Consolidado

- Pontuação Final Normalizada (escala 0–10).
- Classificação conforme tabela de faixas.

---

### 3. Relatório Executivo

- Pontos fortes destacados (ex: indicadores muito positivos).
- Pontos de atenção (ex: divergências entre indicadores).
- Risco/Observação especial se necessário.

✅ Resumo Executivo - Tendência Fundamentalista BTC
🎯 Pontuação Final: 2.17 / 5.0
Classificação: 🟠 Tendência Fraca

🔢 Escala de Avaliação (0 a 5)
Faixa	Pontuação	Cor	Interpretação
🔴 Muito Fraca	0.0 – 1.0	Vermelho	Evitar qualquer exposição
🟠 Fraca	1.1 – 2.5	Laranja	Operar apenas com setups muito seguros
🟡 Moderada	2.6 – 3.5	Amarelo	Risco controlado e seletividade
🔵 Forte	3.6 – 4.4	Azul	Operar com modelo de risco padrão
🟢 Muito Forte	4.5 – 5.0	Verde	Operar com agressividade controlada