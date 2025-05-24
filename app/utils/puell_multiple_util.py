# app/utils/puell_multiple_utils.py
"""
Utilitário para cálculo do Puell Multiple REAL baseado em dados BigQuery
APENAS BigQuery - SEM fallbacks
"""

import logging
import math
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any
from app.config import get_settings

logger = logging.getLogger(__name__)


def safe_float(value, fallback=0.0):
    """Converte valor para float seguro para JSON"""
    try:
        if value is None:
            return fallback
        
        result = float(value)
        
        if math.isnan(result) or math.isinf(result):
            return fallback
            
        return result
    except (TypeError, ValueError):
        return fallback


def safe_division(numerator, denominator, fallback=0.0):
    """Divisão segura que evita NaN, Infinity e None"""
    try:
        if denominator == 0 or denominator is None or numerator is None:
            return fallback
        
        result = numerator / denominator
        
        if math.isnan(result) or math.isinf(result):
            return fallback
            
        return result
    except (TypeError, ZeroDivisionError):
        return fallback


def get_btc_current_price() -> float:
    """
    Busca preço atual do BTC via CoinGecko (para usar no cálculo)
    """
    try:
        import requests
        
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin", "vs_currencies": "usd"}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return safe_float(data.get("bitcoin", {}).get("usd", 0))
        
    except Exception as e:
        logging.error(f"❌ Erro ao buscar preço BTC: {str(e)}")
        return 0.0


def calculate_puell_multiple_bigquery() -> Tuple[float, Dict]:
    """
    Calcula Puell Multiple usando APENAS BigQuery
    
    Fórmula: Receita_Diária_Atual / Média_365_Dias
    Receita = (Reward + Fees) × Preço_BTC
    
    Returns:
        Tuple[float, Dict]: (puell_multiple, metadata)
    """
    try:
        logger.info("🚀 Calculando Puell Multiple via BigQuery...")
        
        # 1. Configurar BigQuery
        settings = get_settings()
        credentials_json = settings.GOOGLE_APPLICATION_CREDENTIALS_JSON
        project_id = settings.GOOGLE_CLOUD_PROJECT
        
        if not credentials_json or not project_id:
            raise Exception("Credenciais Google Cloud não configuradas")
        
        # Importar BigQuery
        from google.cloud import bigquery
        from google.oauth2 import service_account
        
        credentials_info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        client = bigquery.Client(credentials=credentials, project=project_id)
        
        logger.info(f"✅ Cliente BigQuery configurado para projeto: {project_id}")
        
        # 2. Buscar preço atual do BTC
        current_btc_price = get_btc_current_price()
        if current_btc_price <= 0:
            raise Exception("Não foi possível obter preço atual do BTC")
        
        logger.info(f"💰 Preço atual BTC: ${current_btc_price:,.2f}")
        
        # 3. Query BigQuery para receita dos mineradores
        logger.info("⚡ Executando query BigQuery...")
        
        query = """
        WITH daily_mining_data AS (
          SELECT 
            DATE(timestamp) as mining_date,
            COUNT(*) as blocks_mined,
            SUM(reward) / 1e8 as total_btc_reward,
            SUM(fee_satoshi) / 1e8 as total_btc_fees,
            SUM((reward + fee_satoshi)) / 1e8 as total_btc_earned
          FROM `bigquery-public-data.crypto_bitcoin.blocks`
          WHERE 
            DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
            AND reward > 0
          GROUP BY DATE(timestamp)
        ),
        
        daily_revenue AS (
          SELECT 
            mining_date,
            blocks_mined,
            total_btc_earned,
            total_btc_earned * @current_btc_price as revenue_usd
          FROM daily_mining_data
          WHERE total_btc_earned > 0
        )
        
        SELECT 
          mining_date,
          blocks_mined,
          total_btc_earned,
          revenue_usd
        FROM daily_revenue
        ORDER BY mining_date DESC
        """
        
        # Configurar parâmetros da query
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("current_btc_price", "FLOAT64", current_btc_price)
            ]
        )
        
        # Executar query
        result = client.query(query, job_config=job_config).result()
        revenue_data = result.to_dataframe()
        
        if revenue_data.empty or len(revenue_data) < 30:
            raise Exception(f"Dados insuficientes: apenas {len(revenue_data)} dias encontrados")
        
        logger.info(f"📊 Dados coletados: {len(revenue_data)} dias de mineração")
        
        # 4. Calcular Puell Multiple
        revenues = [safe_float(r) for r in revenue_data['revenue_usd'] if r > 0]
        
        if len(revenues) < 30:
            raise Exception("Receitas válidas insuficientes")
        
        revenue_today = revenues[0]  # Mais recente (ORDER BY DESC)
        avg_365 = safe_division(sum(revenues), len(revenues))
        
        puell_multiple = safe_division(revenue_today, avg_365)
        
        # 5. Validar resultado
        if not (0.1 <= puell_multiple <= 10.0):
            raise Exception(f"Puell Multiple fora do range esperado: {puell_multiple}")
        
        # 6. Preparar metadados
        total_btc_mined = safe_float(revenue_data['total_btc_earned'].iloc[0])
        blocks_today = safe_float(revenue_data['blocks_mined'].iloc[0])
        
        metadata = {
            "revenue_today_usd": safe_float(revenue_today),
            "avg_365_days_usd": safe_float(avg_365),
            "btc_price_used": safe_float(current_btc_price),
            "total_btc_mined_today": safe_float(total_btc_mined),
            "blocks_mined_today": safe_float(blocks_today),
            "historical_days": len(revenues),
            "calculation_date": datetime.now().strftime('%Y-%m-%d'),
            "methodology": "BigQuery blockchain data: (reward + fees) × BTC price"
        }
        
        logger.info(f"✅ Puell Multiple calculado: {puell_multiple:.3f}")
        logger.info(f"📈 Receita hoje: ${revenue_today:,.0f}")
        logger.info(f"📊 Média 365 dias: ${avg_365:,.0f}")
        
        return puell_multiple, metadata
        
    except Exception as e:
        logger.error(f"❌ Erro no cálculo BigQuery: {str(e)}")
        raise Exception(f"Falha no BigQuery: {str(e)}")


def _classify_miner_pressure(puell_value: float) -> Tuple[float, str]:
    """
    Classifica a pressão dos mineradores baseado no Puell Multiple
    Score máximo = 10.0
    """
    puell_value = safe_float(puell_value)
    
    if 0.5 <= puell_value <= 1.2:
        return 10.0, "Zona Ideal"
    elif 1.2 < puell_value <= 1.8:
        return 8.0, "Leve Aquecimento"
    elif (0.3 <= puell_value < 0.5) or (1.8 < puell_value <= 2.5):
        return 6.0, "Neutro"
    elif 2.5 < puell_value <= 4.0:
        return 4.0, "Tensão Alta"
    else:
        return 2.0, "Extremo"


def _get_puell_range(puell_value: float) -> str:
    """Retorna a faixa de classificação para Puell Multiple"""
    puell_value = safe_float(puell_value)
    
    if 0.5 <= puell_value <= 1.2:
        return "0.5 - 1.2"
    elif 1.2 < puell_value <= 1.8:
        return "1.2 - 1.8"
    elif (0.3 <= puell_value < 0.5) or (1.8 < puell_value <= 2.5):
        return "0.3-0.5 ou 1.8-2.5"
    elif 2.5 < puell_value <= 4.0:
        return "2.5 - 4.0"
    else:
        return "< 0.3 ou > 4.0"


def get_puell_multiple_analysis() -> Dict[str, Any]:
    """
    Função principal para usar no btc_analysis.py
    Análise completa do Puell Multiple APENAS via BigQuery
    
    Returns:
        Dict: Análise formatada pronta para usar
    """
    try:
        # Calcular Puell Multiple via BigQuery
        puell_value, metadata = calculate_puell_multiple_bigquery()
        
        # Classificar pressão dos mineradores
        score, classificacao = _classify_miner_pressure(puell_value)
        
        return {
            "indicador": "Puell Multiple",
            "fonte": "BigQuery blockchain data (receita real mineradores)",
            "valor_coletado": f"{puell_value:.3f}",
            "score": safe_float(score),
            f"score_ponderado ({score} × 0.20)": safe_float(score * 0.20),
            "classificacao": classificacao,
            "observação": "Ratio da receita diária real dos mineradores vs média de 1 ano (dados blockchain)",
            "detalhes": {
                "dados_coletados": {
                    "puell_value": safe_float(puell_value),
                    "fonte": "BigQuery",
                    "metadata": metadata
                },
                "calculo": {
                    "formula": "Receita_Diária_Mineradores / Média_365_Dias",
                    "resultado": safe_float(puell_value),
                    "faixa_classificacao": _get_puell_range(puell_value)
                },
                "racional": f"Puell de {puell_value:.3f} indica {classificacao.lower()} baseado em dados blockchain reais via BigQuery"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na análise Puell Multiple: {str(e)}")
        
        # SEM FALLBACK - retorna erro
        return {
            "indicador": "Puell Multiple",
            "fonte": "ERRO: BigQuery falhou",
            "valor_coletado": "erro",
            "score": 0.0,
            "score_ponderado (score × peso)": 0.0,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro no BigQuery: {str(e)}. Configure credenciais Google Cloud.",
            "detalhes": {
                "dados_coletados": {
                    "puell_value": 0.0,
                    "fonte": "BigQuery (falhou)"
                },
                "calculo": {
                    "formula": "Receita_Diária_Mineradores / Média_365_Dias",
                    "resultado": 0.0,
                    "faixa_classificacao": "N/A"
                },
                "racional": f"BigQuery indisponível: {str(e)}"
            }
        }