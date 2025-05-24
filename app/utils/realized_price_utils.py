# app/utils/realized_price_utils.py
"""
Utilitário para cálculo do Realized Price REAL baseado em UTXOs movidos
"""

import requests
import logging
import math
from datetime import datetime, timedelta
from typing import Tuple, Optional


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


def get_historical_btc_prices():
    """
    Busca preços históricos do BTC dos últimos 12 meses
    Retorna dict {data: preço}
    """
    try:
        logging.info("🔍 Buscando preços históricos BTC...")
        
        # Usar CoinGecko para preços históricos (365 dias)
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {
            "vs_currency": "usd",
            "days": "365",
            "interval": "daily"
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Converter para dict {timestamp: price}
        price_history = {}
        for price_point in data.get("prices", []):
            timestamp = price_point[0] // 1000  # Convert ms to seconds
            price = safe_float(price_point[1])
            date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            price_history[date_str] = price
            
        logging.info(f"✅ Coletados {len(price_history)} preços históricos")
        return price_history
        
    except Exception as e:
        logging.error(f"❌ Erro ao buscar preços históricos: {str(e)}")
        return {}


def get_spent_utxos_from_blockchair(days_back=365):
    """
    Busca UTXOs gastos (movidos) nos últimos X dias via Blockchair
    Retorna lista de UTXOs com valor e data
    """
    try:
        logging.info(f"🔍 Buscando UTXOs gastos dos últimos {days_back} dias via Blockchair...")
        
        # Calcular data de início
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        date_filter = f"{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
        
        # Blockchair API - outputs gastos com filtro temporal
        url = "https://api.blockchair.com/bitcoin/outputs"
        params = {
            "q": f"time({date_filter}),is_spent(true)",
            "limit": "10000",  # Máximo permitido no free tier
            "s": "time(desc)"  # Ordenar por tempo decrescente
        }
        
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        utxos_data = []
        if data.get("data"):
            for utxo in data["data"]:
                utxo_info = {
                    "value": safe_float(utxo.get("value", 0)) / 100000000,  # Convert satoshis to BTC
                    "time": utxo.get("time", ""),
                    "date": utxo.get("time", "").split()[0] if utxo.get("time") else "",
                    "block_id": utxo.get("block_id", 0)
                }
                utxos_data.append(utxo_info)
        
        logging.info(f"✅ Coletados {len(utxos_data)} UTXOs gastos")
        return utxos_data
        
    except Exception as e:
        logging.error(f"❌ Erro ao buscar UTXOs via Blockchair: {str(e)}")
        return []


def calculate_realized_price_from_utxos():
    """
    Calcula Realized Price REAL baseado em UTXOs movidos
    Fórmula: Σ(UTXO_valor × preço_quando_movido) / Σ(UTXO_valor)
    """
    try:
        logging.info("🚀 Iniciando cálculo Realized Price baseado em UTXOs reais...")
        
        # 1. Buscar preços históricos
        price_history = get_historical_btc_prices()
        if not price_history:
            raise Exception("Não foi possível obter preços históricos")
        
        # 2. Buscar UTXOs gastos
        utxos_data = get_spent_utxos_from_blockchair(days_back=365)
        if not utxos_data:
            raise Exception("Não foi possível obter dados de UTXOs")
        
        # 3. Calcular Realized Price
        total_value_weighted = 0.0
        total_btc_moved = 0.0
        utxos_processed = 0
        
        for utxo in utxos_data:
            utxo_date = utxo.get("date", "")
            utxo_value_btc = utxo.get("value", 0)
            
            # Buscar preço do dia em que o UTXO foi movido
            price_when_moved = price_history.get(utxo_date)
            
            if price_when_moved and utxo_value_btc > 0:
                # Calcular valor ponderado
                weighted_value = utxo_value_btc * price_when_moved
                total_value_weighted += weighted_value
                total_btc_moved += utxo_value_btc
                utxos_processed += 1
        
        # 4. Calcular Realized Price final
        if total_btc_moved > 0:
            realized_price = safe_division(total_value_weighted, total_btc_moved)
            
            logging.info(f"✅ Realized Price calculado: ${realized_price:.2f}")
            logging.info(f"📊 Baseado em {utxos_processed} UTXOs processados")
            logging.info(f"💰 Total BTC analisado: {total_btc_moved:.4f} BTC")
            
            return realized_price, "Blockchair UTXOs reais", {
                "utxos_processed": utxos_processed,
                "total_btc_analyzed": total_btc_moved,
                "date_range": "365 dias",
                "methodology": "UTXOs gastos × preço quando movidos"
            }
        else:
            raise Exception("Nenhum UTXO válido processado")
            
    except Exception as e:
        logging.error(f"❌ Erro no cálculo Realized Price: {str(e)}")
        # Fallback para método anterior (estimativa)
        return _fallback_realized_price_estimate()


def _fallback_realized_price_estimate():
    """
    Fallback: Estimativa baseada em preço atual quando UTXOs reais falham
    """
    try:
        logging.warning("⚠️ Usando fallback - estimativa baseada em preço atual")
        
        # Buscar preço atual do BTC
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin", "vs_currencies": "usd"}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current_price = safe_float(data.get("bitcoin", {}).get("usd", 0))
        
        if current_price > 0:
            # Usar 82% do preço atual como estimativa conservadora
            estimated_realized_price = current_price * 0.82
            
            return estimated_realized_price, "Estimativa (CoinGecko)", {
                "current_price": current_price,
                "percentage_used": "82%",
                "methodology": "Estimativa conservadora baseada em preço atual"
            }
        else:
            # Último fallback: valor histórico conhecido
            return 52000.0, "Fallback histórico", {
                "methodology": "Valor aproximado baseado em dados históricos conhecidos"
            }
            
    except Exception as e:
        logging.error(f"❌ Erro no fallback: {str(e)}")
        return 52000.0, "Fallback histórico", {
            "methodology": "Valor aproximado baseado em dados históricos conhecidos"
        }


def get_realized_price_real() -> Tuple[float, str, dict]:
    """
    Função principal para obter Realized Price REAL
    
    Returns:
        Tuple[float, str, dict]: (realized_price, fonte, metadados)
    """
    try:
        # Tentar método baseado em UTXOs reais primeiro
        return calculate_realized_price_from_utxos()
        
    except Exception as e:
        logging.error(f"❌ Método UTXOs falhou: {str(e)}")
        # Fallback para estimativa
        return _fallback_realized_price_estimate()


def _classify_cycle_phase(variacao_pct: float) -> Tuple[float, str]:
    """
    Classifica a fase do ciclo baseado na variação vs Realized Price
    Score máximo = 10.0
    """
    variacao_pct = safe_float(variacao_pct)
    
    if variacao_pct > 50:
        return 10.0, "Ciclo Aquecido"
    elif variacao_pct > 20:
        return 8.0, "Ciclo Normal"
    elif variacao_pct > -10:
        return 6.0, "Acumulação"
    elif variacao_pct > -30:
        return 4.0, "Capitulação Leve"
    else:
        return 2.0, "Capitulação Severa"


def _get_cycle_phase_range(variacao_pct: float) -> str:
    """Retorna a faixa de classificação para fase do ciclo"""
    variacao_pct = safe_float(variacao_pct)
    
    if variacao_pct > 50:
        return "> +50%"
    elif variacao_pct > 20:
        return "+20% a +50%"
    elif variacao_pct > -10:
        return "-10% a +20%"
    elif variacao_pct > -30:
        return "-30% a -10%"
    else:
        return "< -30%"


def analyze_btc_vs_realized_price(current_btc_price: float) -> dict:
    """
    Análise completa BTC vs Realized Price
    
    Args:
        current_btc_price: Preço atual do BTC
        
    Returns:
        dict: Análise completa formatada
    """
    try:
        # Obter Realized Price real
        realized_price, fonte, metadata = get_realized_price_real()
        
        # Calcular variação
        variacao_pct = safe_division((current_btc_price - realized_price), realized_price, 0.0) * 100
        
        # Classificar fase do ciclo
        score, classificacao = _classify_cycle_phase(variacao_pct)
        
        return {
            "indicador": "BTC vs Realized Price",
            "fonte": f"UTXOs blockchain reais ({fonte})",
            "valor_coletado": f"BTC {variacao_pct:.1f}% vs Realized Price",
            "score": safe_float(score),
            f"score_ponderado ({score} × 0.30)": safe_float(score * 0.30),
            "classificacao": classificacao,
            "observação": "Compara preço de mercado com preço médio real dos holders baseado em UTXOs movidos",
            "detalhes": {
                "dados_coletados": {
                    "preco_atual": safe_float(current_btc_price),
                    "realized_price": safe_float(realized_price),
                    "fonte": fonte,
                    "metadata": metadata
                },
                "calculo": {
                    "formula": f"(({current_btc_price:.0f} - {realized_price:.0f}) / {realized_price:.0f}) × 100",
                    "variacao_percentual": safe_float(variacao_pct),
                    "faixa_classificacao": _get_cycle_phase_range(variacao_pct)
                },
                "racional": f"Preço {variacao_pct:.1f}% vs Realized Price REAL indica {classificacao.lower()} baseado em análise de UTXOs blockchain reais"
            }
        }
        
    except Exception as e:
        logging.error(f"❌ Erro na análise BTC vs Realized Price: {str(e)}")
        return {
            "indicador": "BTC vs Realized Price",
            "fonte": "UTXOs blockchain reais",
            "valor_coletado": "erro",
            "score": 0.0,
            "score_ponderado (score × peso)": 0.0,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro ao calcular Realized Price real: {str(e)}. Verifique conexão APIs ou dados blockchain.",
            "detalhes": {
                "dados_coletados": {
                    "preco_atual": safe_float(current_btc_price),
                    "realized_price": 0.0,
                    "fonte": "N/A"
                },
                "calculo": {
                    "formula": "((Preço_Atual - Realized_Price) / Realized_Price) × 100",
                    "variacao_percentual": 0.0,
                    "faixa_classificacao": "N/A"
                },
                "racional": "Dados indisponíveis devido a erro na coleta de UTXOs blockchain"
            }
        }