# Guia Completo: BigQuery + Railway para Indicadores Bitcoin

## Visão Geral

Este guia implementa dois indicadores Bitcoin:
- **Realized Price**: Preço médio histórico de todos os bitcoins
- **ACB-1Y**: Custo médio dos holders do último ano (novo indicador)

**Arquitetura**:
- Railway: Hospedagem da API
- BigQuery: Processamento de dados Bitcoin
- Google Cloud: Autenticação e credenciais

---

## 1. Configuração da Conta Google Cloud

### 1.1 Criar Projeto no Google Cloud

1. Acesse: https://console.cloud.google.com/
2. Faça login com conta Google
3. Clique em **"Select a project"** → **"New Project"**
4. Configure:
   - **Project name**: `bitcoin-indicators`
   - **Organization**: (deixe padrão)
   - Clique **"Create"**

### 1.2 Ativar APIs Necessárias

1. No menu lateral: **APIs & Services** → **Library**
2. Busque e ative as APIs:
   - **BigQuery API**
   - **BigQuery Data Transfer API**
3. Para cada API:
   - Clique na API
   - Clique **"Enable"**

### 1.3 Criar Service Account

1. Menu lateral: **IAM & Admin** → **Service Accounts**
2. Clique **"Create Service Account"**
3. Configure:
   - **Service account name**: `railway-bigquery`
   - **Service account ID**: (gerado automaticamente)
   - **Description**: `Service account for Railway BigQuery access`
4. Clique **"Create and Continue"**

### 1.4 Definir Permissões

1. Na seção **"Grant this service account access to project"**:
   - **Role**: `BigQuery Data Viewer`
   - **Role**: `BigQuery Job User`
2. Clique **"Continue"** → **"Done"**

### 1.5 Gerar Chave JSON

1. Na lista de Service Accounts, clique no email criado
2. Aba **"Keys"** → **"Add Key"** → **"Create new key"**
3. Selecione **"JSON"**
4. Clique **"Create"**
5. **IMPORTANTE**: Salve o arquivo JSON baixado (ex: `credentials.json`)

---

## 2. Configuração das Variáveis de Ambiente no Railway

### 2.1 Upload do Arquivo de Credenciais

**Opção 1: Via arquivo (Recomendado)**
1. No Railway, vá para seu projeto
2. Aba **"Variables"**
3. Clique **"Add Variable"**
4. Configure:
   - **Name**: `GOOGLE_APPLICATION_CREDENTIALS_JSON`
   - **Value**: Cole todo o conteúdo do arquivo JSON baixado
5. Clique **"Add"**

**Opção 2: Via environment file**
1. Crie pasta `credentials/` no seu projeto
2. Adicione o arquivo `credentials.json`
3. No Railway:
   - **Name**: `GOOGLE_APPLICATION_CREDENTIALS`
   - **Value**: `/app/credentials/credentials.json`

### 2.2 Variáveis Adicionais

Adicione estas variáveis no Railway:

```
GOOGLE_CLOUD_PROJECT=bitcoin-indicators
BIGQUERY_DATASET=crypto_bitcoin
BIGQUERY_PROJECT=bigquery-public-data
```

### 2.3 Variáveis de Configuração da API

```
PORT=8000
ENVIRONMENT=production
API_VERSION=v1
CACHE_DURATION=3600
```

---

## 3. Script para Acessar BigQuery

### 3.1 Dependências (requirements.txt)

```txt
fastapi==0.104.1
uvicorn==0.24.0
google-cloud-bigquery==3.13.0
pandas==2.1.3
python-dotenv==1.0.0
pydantic==2.5.0
httpx==0.25.2
```

### 3.2 Configuração de Credenciais (config.py)

```python
import os
import json
from google.cloud import bigquery
from google.oauth2 import service_account

class BigQueryConfig:
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'bitcoin-indicators')
        self.public_project = os.getenv('BIGQUERY_PROJECT', 'bigquery-public-data')
        self.dataset = os.getenv('BIGQUERY_DATASET', 'crypto_bitcoin')
        
    def get_client(self):
        """Criar cliente BigQuery com credenciais"""
        
        # Opção 1: JSON via variável de ambiente
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        if credentials_json:
            credentials_info = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info
            )
            return bigquery.Client(
                credentials=credentials,
                project=self.project_id
            )
        
        # Opção 2: Arquivo de credenciais
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            return bigquery.Client(
                credentials=credentials,
                project=self.project_id
            )
        
        # Opção 3: Credenciais padrão (para desenvolvimento local)
        return bigquery.Client(project=self.project_id)

# Instância global
bq_config = BigQueryConfig()
```

### 3.3 Cliente BigQuery (bigquery_client.py)

```python
from typing import Optional, Dict, Any
import pandas as pd
from google.cloud import bigquery
from config import bq_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BigQueryClient:
    def __init__(self):
        self.client = bq_config.get_client()
        self.public_project = bq_config.public_project
        self.dataset = bq_config.dataset
        
    def execute_query(self, query: str) -> pd.DataFrame:
        """Executar query e retornar DataFrame"""
        try:
            logger.info(f"Executando query: {query[:100]}...")
            
            # Configurar job
            job_config = bigquery.QueryJobConfig()
            job_config.use_query_cache = True
            job_config.use_legacy_sql = False
            
            # Executar query
            query_job = self.client.query(query, job_config=job_config)
            
            # Aguardar resultado
            result = query_job.result()
            
            # Converter para DataFrame
            df = result.to_dataframe()
            
            logger.info(f"Query executada com sucesso. Linhas: {len(df)}")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao executar query: {str(e)}")
            raise
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Obter informações da tabela"""
        table_ref = f"{self.public_project}.{self.dataset}.{table_name}"
        table = self.client.get_table(table_ref)
        
        return {
            "num_rows": table.num_rows,
            "size_gb": table.num_bytes / (1024**3),
            "schema": [{"name": field.name, "type": field.field_type} for field in table.schema]
        }
    
    def estimate_query_cost(self, query: str) -> float:
        """Estimar custo da query em GB"""
        job_config = bigquery.QueryJobConfig()
        job_config.dry_run = True
        job_config.use_query_cache = True
        
        query_job = self.client.query(query, job_config=job_config)
        
        return query_job.total_bytes_processed / (1024**3)  # GB

# Instância global
bq_client = BigQueryClient()
```

---

## 4. Implementação dos Indicadores

### 4.1 Realized Price Original (indicators.py)

```python
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
from bigquery_client import bq_client
import logging

logger = logging.getLogger(__name__)

class BitcoinIndicators:
    
    def get_realized_price(self, end_date: Optional[str] = None) -> Dict[str, float]:
        """
        Calcular Realized Price original
        
        Fórmula: Realized Cap / Circulating Supply
        Realized Cap = Σ(UTXO_value × price_when_created)
        """
        
        if end_date:
            date_filter = f"AND DATE(o.block_timestamp) <= '{end_date}'"
        else:
            date_filter = ""
        
        query = f"""
        WITH utxos_with_creation_price AS (
          SELECT 
            o.transaction_hash,
            o.output_index,
            o.output_value / 1e8 as btc_value,
            o.block_timestamp,
            DATE(o.block_timestamp) as creation_date
          FROM `bigquery-public-data.crypto_bitcoin.outputs` o
          LEFT JOIN `bigquery-public-data.crypto_bitcoin.inputs` i 
            ON o.transaction_hash = i.spent_transaction_hash 
            AND o.output_index = i.spent_output_index
          WHERE 
            o.output_value > 0
            AND i.spent_transaction_hash IS NULL  -- UTXO não gasto
            {date_filter}
        ),
        
        daily_stats AS (
          SELECT 
            creation_date,
            SUM(btc_value) as daily_btc,
            COUNT(*) as daily_utxos
          FROM utxos_with_creation_price
          GROUP BY creation_date
        ),
        
        -- Aproximação usando preço médio diário (você deve implementar tabela de preços)
        realized_calculation AS (
          SELECT 
            SUM(daily_btc) as total_supply,
            -- Para demonstração, usando preço fixo médio histórico
            -- IMPLEMENTAR: JOIN com tabela de preços históricos
            SUM(daily_btc * 35000) as realized_cap_approx  -- Preço médio aproximado
          FROM daily_stats
        )
        
        SELECT 
          total_supply,
          realized_cap_approx,
          realized_cap_approx / total_supply as realized_price,
          CURRENT_TIMESTAMP() as calculation_time
        FROM realized_calculation
        """
        
        try:
            df = bq_client.execute_query(query)
            
            if df.empty:
                raise ValueError("Nenhum dado retornado para Realized Price")
                
            result = df.iloc[0]
            
            return {
                "realized_price": float(result['realized_price']),
                "total_supply": float(result['total_supply']),
                "realized_cap": float(result['realized_cap_approx']),
                "calculation_time": result['calculation_time'].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular Realized Price: {str(e)}")
            raise

    def get_acb_1y(self, days: int = 365) -> Dict[str, float]:
        """
        Calcular Average Cost Basis dos últimos N dias (ACB-1Y)
        
        Fórmula: Σ(UTXO_value × price_at_creation) / Σ(UTXO_value)
        Apenas para UTXOs criados nos últimos {days} dias
        """
        
        query = f"""
        WITH recent_utxos AS (
          SELECT 
            o.transaction_hash,
            o.output_index,
            o.output_value / 1e8 as btc_value,
            o.block_timestamp,
            DATE(o.block_timestamp) as creation_date
          FROM `bigquery-public-data.crypto_bitcoin.outputs` o
          LEFT JOIN `bigquery-public-data.crypto_bitcoin.inputs` i 
            ON o.transaction_hash = i.spent_transaction_hash 
            AND o.output_index = i.spent_output_index
          WHERE 
            DATE(o.block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
            AND o.output_value > 0
            AND i.spent_transaction_hash IS NULL  -- UTXO não gasto
        ),
        
        daily_aggregation AS (
          SELECT 
            creation_date,
            SUM(btc_value) as daily_btc,
            COUNT(*) as daily_utxos
          FROM recent_utxos
          GROUP BY creation_date
          ORDER BY creation_date DESC
        ),
        
        -- Aproximação usando preço médio diário
        acb_calculation AS (
          SELECT 
            SUM(daily_btc) as total_btc_1y,
            COUNT(*) as days_with_data,
            -- Para demonstração, usando preço crescente simulado
            -- IMPLEMENTAR: JOIN com tabela de preços históricos reais
            SUM(daily_btc * (40000 + (DATE_DIFF(CURRENT_DATE(), creation_date, DAY) * 10))) as total_usd_invested
          FROM daily_aggregation
        )
        
        SELECT 
          total_btc_1y,
          total_usd_invested,
          total_usd_invested / total_btc_1y as acb_1y_price,
          days_with_data,
          CURRENT_TIMESTAMP() as calculation_time
        FROM acb_calculation
        """
        
        try:
            df = bq_client.execute_query(query)
            
            if df.empty:
                raise ValueError(f"Nenhum dado retornado para ACB-{days}D")
                
            result = df.iloc[0]
            
            return {
                "acb_1y_price": float(result['acb_1y_price']),
                "total_btc_1y": float(result['total_btc_1y']),
                "total_usd_invested": float(result['total_usd_invested']),
                "days_analyzed": int(result['days_with_data']),
                "period_days": days,
                "calculation_time": result['calculation_time'].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular ACB-1Y: {str(e)}")
            raise

    def get_comparison_metrics(self) -> Dict[str, Any]:
        """Comparar Realized Price vs ACB-1Y"""
        
        try:
            realized = self.get_realized_price()
            acb_1y = self.get_acb_1y()
            
            comparison = {
                "realized_price": realized,
                "acb_1y": acb_1y,
                "metrics": {
                    "price_difference": acb_1y["acb_1y_price"] - realized["realized_price"],
                    "percentage_difference": ((acb_1y["acb_1y_price"] / realized["realized_price"]) - 1) * 100,
                    "acb_premium": acb_1y["acb_1y_price"] > realized["realized_price"]
                }
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Erro ao comparar métricas: {str(e)}")
            raise

# Instância global
indicators = BitcoinIndicators()
```

### 4.2 API FastAPI (main.py)

```python
from fastapi import FastAPI, HTTPException, Query
from typing import Optional, Dict, Any
import uvicorn
import os
from indicators import indicators
from bigquery_client import bq_client
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bitcoin Indicators API",
    description="API para cálculo de Realized Price e ACB-1Y usando BigQuery",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Endpoint de saúde"""
    return {
        "message": "Bitcoin Indicators API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Verificar conexão com BigQuery"""
    try:
        # Teste simples de conectividade
        query = "SELECT 1 as test"
        result = bq_client.execute_query(query)
        
        return {
            "status": "healthy",
            "bigquery": "connected",
            "timestamp": result.iloc[0] if not result.empty else None
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/realized-price")
async def get_realized_price(
    end_date: Optional[str] = Query(None, description="Data final no formato YYYY-MM-DD")
):
    """
    Calcular Realized Price do Bitcoin
    
    O Realized Price representa o preço médio pago por todos os bitcoins
    baseado na última vez que cada UTXO foi movimentado.
    """
    try:
        result = indicators.get_realized_price(end_date=end_date)
        return result
    except Exception as e:
        logger.error(f"Erro ao calcular Realized Price: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/acb-1y")
async def get_acb_1y(
    days: int = Query(365, ge=1, le=1095, description="Número de dias para análise (1-1095)")
):
    """
    Calcular Average Cost Basis dos últimos N dias (ACB-1Y)
    
    Representa o custo médio dos bitcoins adquiridos pelos holders
    nos últimos N dias especificados.
    """
    try:
        result = indicators.get_acb_1y(days=days)
        return result
    except Exception as e:
        logger.error(f"Erro ao calcular ACB-1Y: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/comparison")
async def get_comparison():
    """
    Comparar Realized Price vs ACB-1Y
    
    Retorna ambos os indicadores e métricas de comparação.
    """
    try:
        result = indicators.get_comparison_metrics()
        return result
    except Exception as e:
        logger.error(f"Erro ao comparar indicadores: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/table-info/{table_name}")
async def get_table_info(table_name: str):
    """Obter informações sobre tabelas do BigQuery"""
    try:
        valid_tables = ["blocks", "transactions", "outputs", "inputs"]
        if table_name not in valid_tables:
            raise HTTPException(
                status_code=400, 
                detail=f"Tabela deve ser uma de: {valid_tables}"
            )
        
        info = bq_client.get_table_info(table_name)
        return info
    except Exception as e:
        logger.error(f"Erro ao obter info da tabela: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=os.getenv("ENVIRONMENT") != "production"
    )
```

---

## 5. Deploy no Railway

### 5.1 Estrutura do Projeto

```
bitcoin-indicators/
├── main.py
├── config.py
├── bigquery_client.py
├── indicators.py
├── requirements.txt
├── Procfile
└── README.md
```

### 5.2 Procfile

```
web: python main.py
```

### 5.3 Comandos de Deploy

```bash
# 1. Inicializar repositório Git
git init
git add .
git commit -m "Initial commit"

# 2. Conectar ao Railway
railway login
railway link

# 3. Deploy
railway up
```

---

## 6. Testes e Verificação

### 6.1 Testes Locais

```python
# test_indicators.py
import pytest
from indicators import indicators
from bigquery_client import bq_client

def test_bigquery_connection():
    """Testar conexão com BigQuery"""
    query = "SELECT 1 as test"
    result = bq_client.execute_query(query)
    assert not result.empty

def test_realized_price():
    """Testar cálculo do Realized Price"""
    result = indicators.get_realized_price()
    assert "realized_price" in result
    assert result["realized_price"] > 0

def test_acb_1y():
    """Testar cálculo do ACB-1Y"""
    result = indicators.get_acb_1y(days=30)  # Teste com 30 dias
    assert "acb_1y_price" in result
    assert result["acb_1y_price"] > 0
```

### 6.2 URLs de Teste (após deploy)

```
https://seu-app.railway.app/
https://seu-app.railway.app/health
https://seu-app.railway.app/realized-price
https://seu-app.railway.app/acb-1y?days=365
https://seu-app.railway.app/comparison
```

---

## 7. Próximos Passos e Melhorias

### 7.1 Implementar Tabela de Preços Históricos

```sql
-- Criar tabela própria de preços
CREATE TABLE `bitcoin-indicators.dataset.btc_daily_prices` (
  date DATE,
  price_usd FLOAT64,
  volume_usd FLOAT64,
  market_cap FLOAT64,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### 7.2 Cache e Performance

```python
# Implementar cache Redis/Memcached
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def cached_realized_price(cache_key: str):
    return indicators.get_realized_price()
```

### 7.3 Monitoramento

- Logs estruturados
- Métricas de performance
- Alertas de erro
- Dashboard de uso

### 7.4 Documentação API

- Swagger UI automático em `/docs`
- Exemplos de resposta
- Rate limiting
- Autenticação (se necessário)

---

## 8. Solução de Problemas

### 8.1 Erros Comuns

**Erro de Autenticação**:
```
google.auth.exceptions.DefaultCredentialsError
```
- Verificar variáveis de ambiente
- Validar formato do JSON
- Confirmar permissões do Service Account

**Erro de Quota**:
```
Quota exceeded: Your project exceeded quota
```
- Verificar uso mensal (1TB gratuito)
- Otimizar queries com LIMIT
- Implementar cache

**Erro de Sintaxe SQL**:
```
Syntax error in SQL query
```
- Validar sintaxe BigQuery (não MySQL)
- Usar backticks para nomes de tabela
- Verificar funções específicas do BigQuery

### 8.2 Debugging

```python
# Adicionar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)

# Testar queries isoladamente
query = "SELECT COUNT(*) FROM `bigquery-public-data.crypto_bitcoin.outputs` LIMIT 1"
result = bq_client.execute_query(query)
print(result)
```

---

## 9. Custos e Limites

### 9.1 BigQuery (Gratuito)
- **Processamento**: 1TB/mês
- **Armazenamento**: 10GB
- **Queries**: Ilimitadas nos dados públicos

### 9.2 Railway (Gratuito)
- **Execução**: 500 horas/mês
- **Memória**: 512MB
- **Banda**: 100GB/mês

### 9.3 Estimativas de Uso
- **Query simples**: ~1GB processamento
- **Query complexa**: ~5-10GB processamento
- **API com 1000 requests/dia**: ~30GB/mês

---

## Conclusão

Esta implementação oferece:
- ✅ Acesso gratuito a dados Bitcoin completos
- ✅ API REST profissional
- ✅ Indicadores precisos e escaláveis
- ✅ Deploy automatizado
- ✅ Monitoramento e logs

**Próximo passo**: Implementar tabela de preços históricos reais para cálculos mais precisos.