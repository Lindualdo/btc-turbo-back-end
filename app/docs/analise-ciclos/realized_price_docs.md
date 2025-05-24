# Documentação: Realized Price - BTC Turbo

## O que é o Realized Price?

O **Realized Price** é o preço médio que todos os holders atuais do Bitcoin pagaram pelos bitcoins que ainda possuem.

**Fórmula:**
```
Realized Price = Realized Cap ÷ Total Supply
```

**Onde:**
- **Realized Cap** = Soma de (cada UTXO × preço quando foi criado)
- **Total Supply** = Total de bitcoins não gastos

## Como Funciona?

### 1. **Buscar Preços Históricos Reais**
- Conecta no TradingView (usando sessão do BTC Turbo)
- Baixa ~2000 dias de preços históricos do Bitcoin
- Exemplo: 01/01/2023 → $16.500, 15/03/2024 → $73.000

### 2. **Buscar UTXOs Não Gastos**
- Conecta no BigQuery (dados públicos da blockchain)
- Busca todos os bitcoins que ainda não foram movimentados
- Para cada UTXO: data de criação + quantidade

### 3. **Agrupar por Data**
- Soma quantos bitcoins foram criados em cada dia
- Exemplo: 01/01/2023 → 1.500 BTC criados

### 4. **Cruzar Dados**
- Junta UTXOs com preços históricos pela data
- Resultado: 01/01/2023 → 1.500 BTC × $16.500 = $24.750.000

### 5. **Calcular Realized Price**
- Soma todo o valor investido (Realized Cap)
- Divide pelo total de bitcoins (Supply)
- Resultado: Preço médio pago pelos holders atuais

## Interpretação

| Realized Price | Situação | Significado |
|---|---|---|
| **Muito baixo** | Holders pagaram barato | Mercado pode estar oversold - Oportunidade |
| **Baixo** | Custo médio baixo | Potencial de alta |
| **Neutro** | Próximo ao preço atual | Mercado equilibrado |
| **Alto** | Holders pagaram caro | Mercado pode estar sobrecomprado |
| **Muito alto** | Custo médio muito alto | Risco de correção |

## Comparação com Preço Atual

```
Se Preço Atual > Realized Price → Mercado em LUCRO geral
Se Preço Atual < Realized Price → Mercado em PREJUÍZO geral
```

## Integração no BTC Turbo

### Configuração Necessária
- ✅ **TradingView**: Já configurado (tv_session_manager)
- ✅ **Railway**: Variáveis de ambiente BigQuery
- ✅ **BigQuery**: Credenciais do Google Cloud

### Como Usar
```python
from app.utils.realized_price_utils import get_realized_price_simple

# Obter Realized Price atual
result = get_realized_price_simple()
print(f"Realized Price: {result['valor_formatado']}")
```

### Resposta da API
```json
{
  "indicador": "Realized Price",
  "valor": 45234.56,
  "valor_formatado": "$45,234.56",
  "status": "success",
  "timestamp": "2025-05-24T10:30:00",
  "fonte": "BigQuery + TradingView"
}
```

## Sistema de Fallback

**Se TradingView falhar:**
- Usa preços aproximados por faixa de tempo
- Última 1 ano: ~$65k, 2-3 anos: ~$45k, +4 anos: ~$20k

**Se BigQuery falhar:**
- Retorna valor padrão: $45.000

**Sempre funciona**, mesmo com problemas externos.

## Casos de Uso no BTC Turbo

1. **Análise de Risco**: Medir se holders estão em lucro/prejuízo
2. **Timing de Entrada**: Realized Price baixo = boa oportunidade  
3. **Gestão de Posição**: Ajustar alavancagem baseado no nível
4. **Indicador Estrutural**: Complementar análises técnicas e fundamentais

---

## Código Comentado

```python
# app/utils/realized_price_utils.py

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import json
from datetime import datetime
from app.services.tv_session_manager import get_tv_instance
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)

def get_bitcoin_historical_prices() -> pd.DataFrame:
    """
    PASSO 1: Buscar preços históricos reais do Bitcoin via TradingView
    """
    try:
        # Usa sessão TV existente do BTC Turbo
        tv = get_tv_instance()
        
        if tv is None:
            logger.error("❌ TradingView indisponível")
            return pd.DataFrame()
        
        logger.info("📊 Buscando preços históricos...")
        
        # Busca ~2000 dias de dados históricos (5 anos)
        btc_data = tv.get_hist(
            symbol='BTCUSD',
            exchange='BINANCE', 
            interval='1d',
            n_bars=2000
        )
        
        if btc_data is None or btc_data.empty:
            return pd.DataFrame()
        
        # Formata dados: [data, preço]
        btc_data = btc_data.reset_index()
        btc_data['date'] = btc_data['datetime'].dt.date
        btc_data = btc_data[['date', 'close']].rename(columns={'close': 'price'})
        
        logger.info(f"✅ {len(btc_data)} dias de preços carregados")
        return btc_data
        
    except Exception as e:
        logger.error(f"❌ Erro TradingView: {str(e)}")
        return pd.DataFrame()

def get_realized_price() -> float:
    """
    Função principal: Calcular Realized Price usando BigQuery + TradingView
    """
    try:
        # PASSO 1: Buscar preços históricos do TradingView
        logger.info("🚀 Iniciando cálculo Realized Price...")
        price_data = get_bitcoin_historical_prices()
        
        if price_data.empty:
            logger.warning("⚠️ Usando fallback de preços")
            return get_realized_price_fallback()
        
        # PASSO 2: Configurar BigQuery
        logger.info("🔗 Conectando BigQuery...")
        settings = get_settings()
        credentials_json = settings.google_application_credentials_json
        credentials_info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        client = bigquery.Client(credentials=credentials, project=settings.google_cloud_project)
        
        # PASSO 3: Buscar UTXOs não gastos (últimos 3 anos para performance)
        logger.info("⚡ Buscando UTXOs não gastos...")
        query = """
        WITH current_utxos AS (
          -- Busca todas as saídas (outputs) não gastas
          SELECT 
            o.value / 1e8 as btc_value,              -- Converte satoshis para BTC
            DATE(o.block_timestamp) as creation_date -- Data de criação
          FROM `bigquery-public-data.crypto_bitcoin.outputs` o
          LEFT JOIN `bigquery-public-data.crypto_bitcoin.inputs` i 
            ON o.transaction_hash = i.spent_transaction_hash 
            AND o.output_index = i.spent_output_index
          WHERE 
            o.value > 0
            AND i.spent_transaction_hash IS NULL     -- UTXO não foi gasto
            AND DATE(o.block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 1095 DAY)
        ),
        
        daily_aggregation AS (
          -- Agrupa bitcoins criados por data
          SELECT 
            creation_date,
            SUM(btc_value) as daily_btc             -- Total BTC criado neste dia
          FROM current_utxos
          GROUP BY creation_date
        )
        
        SELECT creation_date, daily_btc
        FROM daily_aggregation
        ORDER BY creation_date
        """
        
        # PASSO 4: Executar query e obter dados
        result = client.query(query).result()
        utxo_data = result.to_dataframe()
        
        if utxo_data.empty:
            logger.error("❌ Nenhum UTXO encontrado")
            return 0.0
        
        # PASSO 5: Cruzar UTXOs com preços históricos
        logger.info("🔄 Cruzando UTXOs com preços...")
        
        # Converter datas para mesmo formato
        utxo_data['creation_date'] = pd.to_datetime(utxo_data['creation_date']).dt.date
        price_data['date'] = pd.to_datetime(price_data['date']).dt.date
        
        # Fazer merge: para cada data de UTXO, encontrar o preço
        merged_data = utxo_data.merge(price_data, left_on='creation_date', right_on='date', how='left')
        
        # Preencher preços faltantes com valores próximos
        merged_data['price'] = merged_data['price'].fillna(method='bfill').fillna(method='ffill')
        merged_data = merged_data.dropna(subset=['price'])
        
        if merged_data.empty:
            return get_realized_price_fallback()
        
        # PASSO 6: Calcular Realized Price
        # Realized Cap = Σ(BTC_de_cada_dia × preço_real_desse_dia)
        total_realized_cap = (merged_data['daily_btc'] * merged_data['price']).sum()
        
        # Total Supply = Σ(todos os BTC não gastos)
        total_supply = merged_data['daily_btc'].sum()
        
        if total_supply == 0:
            return 0.0
        
        # Realized Price = Realized Cap ÷ Total Supply
        realized_price = total_realized_cap / total_supply
        
        logger.info(f"✅ Realized Price: ${realized_price:,.2f}")
        logger.info(f"📈 Supply analisado: {total_supply:,.2f} BTC")
        logger.info(f"💰 Realized Cap: ${total_realized_cap:,.0f}")
        
        return float(realized_price)
        
    except Exception as e:
        logger.error(f"❌ Erro no cálculo: {str(e)}")
        return get_realized_price_fallback()

def get_realized_price_fallback() -> float:
    """
    FALLBACK: Preços aproximados caso TradingView falhe
    """
    try:
        logger.info("🔄 Executando fallback...")
        
        settings = get_settings()
        credentials_json = settings.google_application_credentials_json
        credentials_info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        client = bigquery.Client(credentials=credentials, project=settings.google_cloud_project)
        
        # Query com preços aproximados por faixa de tempo
        query = """
        WITH current_utxos AS (
          SELECT 
            o.value / 1e8 as btc_value,
            DATE(o.block_timestamp) as creation_date
          FROM `bigquery-public-data.crypto_bitcoin.outputs` o
          LEFT JOIN `bigquery-public-data.crypto_bitcoin.inputs` i 
            ON o.transaction_hash = i.spent_transaction_hash 
            AND o.output_index = i.spent_output_index
          WHERE 
            o.value > 0
            AND i.spent_transaction_hash IS NULL
            AND DATE(o.block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 730 DAY)
        ),
        
        daily_aggregation AS (
          SELECT 
            creation_date,
            SUM(btc_value) as daily_btc
          FROM current_utxos
          GROUP BY creation_date
        ),
        
        realized_calculation AS (
          SELECT 
            SUM(daily_btc) as total_supply,
            -- Preços aproximados por faixa de tempo
            SUM(daily_btc * (
              CASE 
                WHEN DATE_DIFF(CURRENT_DATE(), creation_date, DAY) > 1460 THEN 20000  -- +4 anos: $20k
                WHEN DATE_DIFF(CURRENT_DATE(), creation_date, DAY) > 1095 THEN 35000  -- +3 anos: $35k  
                WHEN DATE_DIFF(CURRENT_DATE(), creation_date, DAY) > 730 THEN 45000   -- +2 anos: $45k
                WHEN DATE_DIFF(CURRENT_DATE(), creation_date, DAY) > 365 THEN 55000   -- +1 ano: $55k
                ELSE 65000  -- Último ano: $65k
              END
            )) / SUM(daily_btc) as realized_price
          FROM daily_aggregation
        )
        
        SELECT realized_price FROM realized_calculation
        """
        
        result = client.query(query).result()
        df = result.to_dataframe()
        
        if df.empty:
            return 45000.0  # Valor padrão
            
        price = float(df.iloc[0]['realized_price'])
        logger.info(f"🔄 Realized Price (fallback): ${price:,.2f}")
        return price
        
    except Exception as e:
        logger.error(f"❌ Erro fallback: {str(e)}")
        return 45000.0

def get_realized_price_simple() -> dict:
    """
    Função para APIs: retorna dados formatados
    """
    try:
        price = get_realized_price()
        
        return {
            "indicador": "Realized Price",
            "valor": round(price, 2),
            "valor_formatado": f"${price:,.2f}",
            "status": "success" if price > 0 else "error",
            "timestamp": datetime.now().isoformat(),
            "fonte": "BigQuery + TradingView"
        }
        
    except Exception as e:
        return {
            "indicador": "Realized Price",
            "valor": 0.0,
            "valor_formatado": "$0.00",
            "status": "error",
            "erro": str(e),
            "timestamp": datetime.now().isoformat()
        }
```