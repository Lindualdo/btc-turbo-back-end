📊 Análise Detalhada do BTC Analysis API
1. Validação das Regras dos Indicadores
✅ BTC vs EMA 200D (30%)

Regras corretas: Classificação por faixas percentuais (>30%, 15-30%, 5-15%, 0-5%, <0%)
Scores adequados: 10.0, 8.0, 6.0, 4.0, 2.0
Peso aplicado: 30% (0.30)

✅ BTC vs Realized Price (30%)

Regras corretas: Faixas de variação percentual bem definidas
Scores adequados: 10.0, 8.0, 6.0, 4.0, 2.0
Peso aplicado: 30% (0.30)

✅ Puell Multiple (20%)

Regras corretas: Faixas numéricas adequadas (0.5-1.2, 1.2-1.8, etc.)
Scores adequados: 10.0, 8.0, 6.0, 4.0, 2.0
Peso aplicado: 20% (0.20)

✅ M2 Global Momentum (15%)

Regras corretas: Faixas de momentum percentual
Scores adequados: 10.0, 8.0, 6.0, 4.0, 2.0
Peso aplicado: 15% (0.15)

✅ Funding Rates 7D (5%)

Regras corretas: Faixas percentuais de funding rates
Scores adequados: 10.0, 8.0, 6.0, 4.0, 2.0
Peso aplicado: 5% (0.05)

2. Dados Fixos no Código
🚨 Problemas Identificados:

M2 fallback: Valor fixo 2.0 usado como fallback em múltiplas funções
Score padrão: 0.0 usado universalmente para erros (pode mascarar problemas)
Timeout: 10 segundos fixo para requests
Límites de dados: 250 barras para EMA, 56 períodos para funding rates
Parâmetros TradingView: Exchange "BINANCE", símbolo "BTCUSDT" fixos

3. Indicadores Usando Notion
🔄 Necessitam Migração:

Puell Multiple: 100% dependente do Notion
M2 Global Momentum: Usa Notion como fallback (função _get_m2_from_notion())

✅ Já Migrados:

BTC vs EMA 200D: TradingView direto
BTC vs Realized Price: Utilitário com UTXOs blockchain
Funding Rates: Binance API direto

4. Campo "detalhes" nos Indicadores
✅ Completos:

BTC vs EMA 200D: ✅ dados_coletados, calculo, racional
BTC vs Realized Price: ✅ estrutura completa
Funding Rates: ✅ estrutura completa

⚠️ Incompletos:

Puell Multiple: ❌ Falta receita_diaria, media_365d nos dados_coletados
M2 Global Momentum: ❌ Falta m2_atual, m2_trimestre_anterior nos dados_coletados

5. Funções Não Utilizadas (Candidatas à Remoção)
🗑️ Obsoletas:

safe_division(): Não está sendo usada em nenhum lugar do código atual
safe_float(): Usada extensivamente - MANTER

⚠️ Investigar:

_get_m2_from_apis(): Chama utilitário externo - verificar se utilitário existe
_get_m2_from_notion(): Ainda em uso como fallback

6. Funções Duplicadas/Redundantes
🔄 M2 Global:

get_m2_global_momentum(): Função principal (linha ~215)
_get_m2_from_apis(): Helper que chama utilitário externo
_get_m2_from_notion(): Fallback do Notion
Duplicação: Existe get_m2_global_momentum() importado de app.utils.m2_utils

7. Utilizar Utils para reduzir o tamanho do arquivo btc_analisys.py
- será usado apenas como proxy deixando em cada Util a função principal com calculos de cada indicador
- validar a fução BTC X Realized Price (dados estão mesmo dinamicos?)


🔄 Realized Price:

get_btc_vs_realized_price(): Função principal atual
analyze_btc_vs_realized_price(): Importado de utilitário externo
Status: Migração já iniciada, função principal chama o utilitário

📋 Resumo Executivo
Prioridades para Refatoração:

🔴 CRÍTICO: Substituir dependência do Notion no Puell Multiple
🟡 IMPORTANTE: Completar migração do M2 Global (remover fallback Notion)
🟢 MELHORIA: Completar campos "detalhes" nos indicadores incompletos
🟢 LIMPEZA: Remover função safe_division() não utilizada
🟢 ORGANIZAÇÃO: Consolidar funções duplicadas do M2 Global

Indicadores Prontos: 3/5 (BTC vs EMA, Realized Price, Funding Rates)
Indicadores Pendentes: 2/5 (Puell Multiple, M2 Global - dependem do Notion)
Próximo Passo Recomendado: Migrar Puell Multiple para fonte de dados dinâmica (Glassnode API ou similar).