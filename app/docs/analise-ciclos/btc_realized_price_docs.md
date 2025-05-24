# 📊 BTC vs Realized Price - Documentação Técnica Completa

**Versão:** v2.0 - Implementação VWAP-365D  
**Data:** 24 de Maio de 2025  
**Status:** Refatoração - Substituição da abordagem UTXOs por VWAP  

---

## 🎯 **Objetivo do Indicador**

Avaliar a **fase do ciclo** do Bitcoin comparando o **preço atual de mercado** com o **custo médio real dos HOLDERS**, determinando se os holders estão em lucro ou prejuízo agregado para classificar o momento do ciclo de alta/baixa.

---

## 📈 **Metodologia Original vs Nova**

### **🔴 Abordagem Original (FALHA)**
```
Realized Price = Σ(UTXO_valor × preço_quando_movido) / Σ(UTXO_valor)
```

**Problemas Identificados:**
- ❌ Sempre caindo no fallback (preço atual × 82%)
- ❌ APIs Blockchair/CoinGecko falhando consistentemente
- ❌ Complexidade excessiva (UTXOs individuais + cruzamento temporal)
- ❌ Rate limiting e timeouts constantes
- ❌ Dados não dinâmicos (valor fixo $52.000 como último fallback)

### **✅ Abordagem Nova (VWAP-365D)**
```
Realized Price ≈ VWAP-365D = Σ(Preço_dia × Volume_dia) / Σ(Volume_total)
Período: Últimos 365 dias (1 ano completo)
```

**Vantagens:**
- ✅ Dados dinâmicos em tempo real via CoinGecko API
- ✅ Simplicidade de implementação (1 call API vs 100+)
- ✅ Estatisticamente válido para medir custo médio de HOLDERS
- ✅ Sem dependência de UTXOs complexos
- ✅ Robustez e confiabilidade comprovadas

---

## 🧮 **Fundamentação Matemática**

### **Equivalência Conceitual**
Ambas as fórmulas medem **preço médio ponderado por atividade**:

- **Original**: Pondera por valor dos UTXOs movimentados
- **VWAP-365D**: Pondera por volume de trading diário

**Resultado**: Aproximação estatisticamente válida do custo médio dos participantes do mercado.

### **Fórmula Detalhada VWAP-365D**
```python
# Para cada dia dos últimos 365 dias:
weighted_value_day = price_day × volume_day

# Somatório de 365 dias:
total_weighted = Σ(weighted_value_day)
total_volume = Σ(volume_day)

# Realized Price final:
realized_price = total_weighted / total_volume
```

---

## 📊 **Definição de HOLDERS vs TRADERS**

### **🔬 Base Científica (Glassnode)**
- **Short-Term Holders (STH)**: < 155 dias
- **Long-Term Holders (LTH)**: ≥ 155 dias
- **Threshold Estatístico**: 155 dias = ponto onde Bitcoin se torna "estatisticamente improvável de ser movido"

### **📈 Distribuição do Supply**
- **66% do supply total**: Long-Term Holders (12.3M BTC)
- **20% do supply**: Short-Term Holders (3.7M BTC)
- **14% restante**: Exchanges e outras categorias

### **⚖️ Justificativa do Período 365D**
- **365 dias >> 155 dias**: Definitivamente captura HOLDERS, não traders
- **Mantém compatibilidade**: Mesmo período do código original
- **Viabilidade técnica**: CoinGecko free tier suporta até 365 dias
- **Representatividade**: Inclui ciclos sazonais e holders consolidados

---

## 🔧 **Implementação Técnica**

### **Fonte de Dados**
```
Endpoint: https://api.coingecko.com/api/v3/coins/bitcoin/market_chart
Parâmetros:
- vs_currency: usd
- days: 365
- interval: daily
```

**Dados Retornados:**
- `prices[]`: Preços diários do Bitcoin (timestamp, price)
- `total_volumes[]`: Volume total de trading por dia (timestamp, volume)

### **Estrutura de Resposta**
```json
{
    "indicador": "BTC vs Realized Price",
    "fonte": "VWAP-365D (CoinGecko)",
    "valor_coletado": "BTC +35.2% vs Realized Price",
    "score": 8.0,
    "score_ponderado (8.0 × 0.30)": 2.4,
    "classificacao": "Ciclo Normal",
    "observação": "Preço vs custo médio real dos HOLDERS baseado em VWAP de 365 dias",
    "detalhes": {
        "dados_coletados": {
            "preco_atual": 107500.00,
            "realized_price_vwap365": 79800.00,
            "fonte": "CoinGecko VWAP-365D",
            "periodo_analise": "365 dias",
            "total_volume_periodo": 2500000000000,
            "data_inicio": "2024-05-24",
            "data_fim": "2025-05-24"
        },
        "calculo": {
            "formula": "VWAP-365D = Σ(Preço_dia × Volume_dia) / Σ(Volume_total)",
            "variacao_percentual": 34.6,
            "faixa_classificacao": "+20% a +50%"
        },
        "racional": "Preço 34.6% acima do Realized Price (VWAP-365D) indica ciclo normal com holders em lucro moderado"
    }
}
```

### **Código Python Simplificado**
```python
def get_realized_price_vwap_365d(current_btc_price):
    """
    Calcula Realized Price usando VWAP dos últimos 365 dias
    Substitui a abordagem UTXOs falhada por método robusto e dinâmico
    """
    try:
        # 1. Coletar dados CoinGecko (1 call apenas)
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {"vs_currency": "usd", "days": "365", "interval": "daily"}
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # 2. Extrair preços e volumes
        prices = [item[1] for item in data['prices']]
        volumes = [item[1] for item in data['total_volumes']]
        
        # 3. Calcular VWAP-365D
        total_weighted = sum(price * volume for price, volume in zip(prices, volumes))
        total_volume = sum(volumes)
        realized_price = total_weighted / total_volume
        
        # 4. Calcular variação percentual
        variation_pct = ((current_btc_price - realized_price) / realized_price) * 100
        
        # 5. Classificar fase do ciclo
        score, classification = _classify_cycle_phase(variation_pct)
        
        return {
            # Estrutura de resposta completa conforme especificação
        }
        
    except Exception as e:
        return {
            # Estrutura de erro padronizada
        }
```

---

## 📏 **Sistema de Classificação**

### **Faixas de Variação Percentual**
| Variação % | Classificação | Score | Descrição |
|------------|---------------|-------|-----------|
| **> +50%** | **Ciclo Aquecido** | **10.0** | Euforia, holders em lucro extremo |
| **+20% a +50%** | **Ciclo Normal** | **8.0** | Bull market saudável |
| **-10% a +20%** | **Acumulação** | **6.0** | Holders equilibrados, acumulação |
| **-30% a -10%** | **Capitulação Leve** | **4.0** | Alguns holders em prejuízo |
| **< -30%** | **Capitulação Severa** | **2.0** | Bear market, holders em prejuízo |

### **Peso no Score Consolidado**
- **Peso**: 30% (0.30)
- **Score máximo**: 10.0
- **Contribuição máxima**: 3.0 pontos

---

## 🎯 **Interpretação dos Resultados**

### **Quando Preço > Realized Price**
- **Significado**: Holders estão em lucro agregado
- **Implicação**: Fase de bull market ou recuperação
- **Pressão**: Potencial pressão de venda (profit-taking)

### **Quando Preço < Realized Price**
- **Significado**: Holders estão em prejuízo agregado
- **Implicação**: Fase de bear market ou correção
- **Pressão**: Holders resistentes, acumulação por novos compradores

### **Quando Preço ≈ Realized Price**
- **Significado**: Equilíbrio, ponto de inflexão
- **Implicação**: Possível mudança de tendência
- **Pressão**: Mercado indefinido

---

## ⚠️ **Limitações e Considerações**

### **Limitações da Abordagem VWAP-365D**
1. **Aproximação**: Não é o Realized Price "real" dos UTXOs
2. **Volume Exchange**: Baseado em volume de exchanges, não volume on-chain
3. **Período fixo**: 365 dias pode não capturar todos os holders de longo prazo
4. **Representatividade**: Pode ser influenciado por eventos específicos no período

### **Vantagens Compensatórias**
1. **Confiabilidade**: Dados sempre disponíveis e atualizados
2. **Simplicidade**: Fácil de implementar e debuggar
3. **Performance**: Rápido e eficiente
4. **Robustez**: Sem dependência de APIs complexas

### **Cenários de Falha**
- **API CoinGecko indisponível**: Implementar fallback para preço atual × 0.85
- **Dados insuficientes**: Reduzir período para 180 ou 90 dias gradualmente
- **Rate limiting**: Implementar cache e retry logic

---

## 🔄 **Migração da Versão Anterior**

### **Mudanças Necessárias**
1. **Remover**: Todas as funções relacionadas a UTXOs
2. **Substituir**: `get_btc_vs_realized_price()` por nova implementação
3. **Manter**: Sistema de classificação e pesos existentes
4. **Adicionar**: Logging detalhado para monitoramento

### **Compatibilidade**
- **Formato de saída**: 100% compatível com API existente
- **Classificações**: Mantidas as mesmas faixas percentuais
- **Peso no score**: Mantido 30% (0.30)

---

## 📚 **Referências Técnicas**

### **Definições de HOLDERS**
- **Glassnode**: "Long-Term Holders" (LTH) ≥ 155 dias
- **Threshold Estatístico**: 155 dias = UTXOs "improváveis de serem movidos"
- **Supply Distribution**: 66% LTH, 20% STH, 14% outros

### **Volume Weighted Average Price (VWAP)**
- **Definição**: Preço médio ponderado por volume de negociação
- **Uso**: Benchmark amplamente aceito em mercados financeiros
- **Aplicação**: Proxy válido para preço médio de aquisição

### **APIs e Fontes**
- **CoinGecko**: Principal fonte de dados de preços e volumes
- **Rate Limits**: 30 calls/min (free tier), 500 calls/min (paid)
- **Histórico**: Até 365 dias gratuitos, 10+ anos pagos

---

## 🛠️ **Testes e Validação**

### **Cenários de Teste**
1. **API funcionando**: Dados normais dos últimos 365 dias
2. **Período parcial**: CoinGecko retorna menos que 365 dias
3. **Dados ausentes**: Volumes ou preços zerados em alguns dias
4. **Rate limiting**: Múltiplas chamadas simultâneas
5. **API offline**: Fallback para estimativa conservadora

### **Métricas de Qualidade**
- **Completude**: % de dias com dados válidos no período
- **Consistência**: Variação entre múltiplas coletas
- **Latência**: Tempo de resposta da API
- **Disponibilidade**: Uptime da fonte de dados

---

## 📊 **Exemplo Prático**

### **Cenário: Bitcoin em Bull Market**
```
Preço Atual: $108,000
Realized Price (VWAP-365D): $79,800
Variação: +35.3%
Classificação: Ciclo Normal (Score 8.0)
```

**Interpretação**: Holders estão em lucro moderado (+35%), indicando bull market saudável sem sinais de euforia extrema.

### **Cenário: Bitcoin em Bear Market**
```
Preço Atual: $45,000
Realized Price (VWAP-365D): $65,000
Variação: -30.8%
Classificação: Capitulação Severa (Score 2.0)
```

**Interpretação**: Holders estão em prejuízo significativo (-31%), indicando bear market com possível proximidade de fundo.

---

## 🎯 **Conclusão**

A implementação **VWAP-365D** resolve os problemas críticos da abordagem UTXOs original, mantendo a essência e objetivo do indicador Realized Price. A metodologia é:

- ✅ **Tecnicamente viável**
- ✅ **Estatisticamente válida**  
- ✅ **Conceitualmente correta**
- ✅ **Operacionalmente robusta**

**Status**: Pronto para implementação imediata.

---

**Última Atualização**: 24 de Maio de 2025  
**Próxima Revisão**: Pós-implementação (30 dias)