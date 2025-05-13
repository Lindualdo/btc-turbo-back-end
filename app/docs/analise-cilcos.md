# 🎯 Analise Ciclos

---

## 🎯 Objetivo

Confirmar de forma **objetiva e quantitativa** se o mercado do Bitcoin está em **Bull Market** ou **Bear Market**, avaliando também a **força do ciclo**.

---

## 🧩 Indicadores Utilizados e Pesos

| Indicador | Peso (%) | Fonte de Dados |
| --- | --- | --- |
| **BTC preço vs 200D EMA** | 25% | TradingView |
| **BTC preço vs Realized Price** | 25% | LookIntoBitcoin / Glassnode |
| **Puell Multiple** | 20% | LookIntoBitcoin / Glassnode |
| **BTC Dominance Tendência** | 20% | TradingView |
| **Macro Ambiente (Liquidez e Juros)** | 10% | FRED, fontes econômicas confiáveis |

---

## 📝 Template de Entrada (Coleta de Dados)

| Indicador | Valor Atual | Escala de Avaliação | Pontuação Bruta | Peso | Pontuação Ponderada |
| --- | --- | --- | --- | --- | --- |
| BTC preço vs 200D EMA | (ex: 12% acima) | >10% acima = +2 / 0–10% acima = +1 / Abaixo = 0 |  | 25% |  |
| BTC preço vs Realized Price | (ex: 18% acima) | >15% acima = +2 / 0–15% acima = +1 / Abaixo = 0 |  | 25% |  |
| Puell Multiple | (ex: 0.9) | 0.3–1.5 = +2 / 1.5–2.5 = +1 / Fora disso = 0 |  | 20% |  |
| BTC Dominance Tendência | (ex: Subindo) | Tendência de alta = +2 / Estável = +1 / Queda = 0 |  | 20% |  |
| Macro Ambiente (Liquidez/Juros) | (ex: Expansão 3.8%) | Expansão >3% = +2 / Estável = +1 / Restritivo = 0 |  | 10% |  |

---

## 🧮 Cálculo

- Pontuação Total Máxima: 2.0 (se tudo for pontuação máxima).
- Fórmula da Pontuação Final Normalizada:
    
    `(Pontuação Obtida / 2.0) × 10`
    

---

## 📊 Faixas de Interpretação (5 Escalas)

| Pontuação Final | Interpretação | Estratégia |
| --- | --- | --- |
| 0.0–2.0 | 🔴 Bear Forte | Defesa máxima (nada de novas operações) |
| 2.1–4.0 | 🟠 Bear Leve | Atenção / Exposição mínima |
| 4.1–6.0 | 🟡 Tendência Neutra | Analisar com cautela, pouca exposição |
| 6.1–8.0 | 🔵 Bull Moderado | Operar com tamanho controlado |
| 8.1–10.0 | 🟢 Bull Forte | Operar agressivamente |

---

## 📎 Padrão de Entrega Executiva

### 1. Dados Individuais

Tabela preenchida com:

- Valor atual de cada indicador
- Pontuação Bruta
- Peso
- Pontuação Ponderada

---

### 2. Resultado Consolidado

- Pontuação Total Normalizada (escala 0–10)
- Classificação de Tendência
- Estratégia correspondente.

---

### 3. Relatório Executivo

- Destacar:
    - Indicadores mais fortes ou mais fracos.
    - Divergências relevantes.
    - Observações de risco/mudanças potenciais.

---

## 🕒 Frequência de Atualização

- Atualizar **semanalmente**.
- Ou imediatamente após:
    - Variações >10% no preço do BTC.
    - Mudanças macroeconômicas relevantes.

---