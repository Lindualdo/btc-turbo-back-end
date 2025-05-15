# app/services/risk_analysis_rsi.py

from app.services.tv_session_manager import get_tv_instance
from app.utils.rsi_utils import calcular_rsi, analisar_rsi_risco
from tvDatafeed import Interval
import pandas as pd
from typing import Dict, Any, List, Tuple

interval_map = {
    "15m": Interval.in_15_minute,
    "30m": Interval.in_30_minute,
    "1h": Interval.in_1_hour,
    "4h": Interval.in_4_hour,
    "1d": Interval.in_daily,
    "1w": Interval.in_weekly
}

rsi_periodo = 14

def get_rsi_data() -> Dict[str, float]:
    """
    Obtém os dados de RSI de todos os timeframes
    
    Returns:
        Dicionário com valores RSI por timeframe
    """
    tv = get_tv_instance()
    rsi_values = {}
    
    for key, interval in interval_map.items():
        try:
            df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=interval, n_bars=500)
            
            if not isinstance(df, pd.DataFrame) or df.empty:
                continue
                
            df = calcular_rsi(df, periodo=rsi_periodo)
            latest = df.iloc[-1]
            
            if "RSI" in latest and not pd.isna(latest["RSI"]):
                rsi_values[key] = latest["RSI"]
                
        except Exception:
            # Silently continue if we can't get data for a timeframe
            continue
    
    return rsi_values

def calculate_rsi_risk() -> Dict[str, Any]:
    """
    Calcula o componente de risco RSI sobrecomprado para análise de risco técnico
    
    Returns:
        Componente de risco RSI para a análise técnica
    """
    try:
        # Obter valores RSI
        rsi_values = get_rsi_data()
        
        # Analisar risco com base nos valores de RSI
        analise = analisar_rsi_risco(rsi_values)
        
        return {
            "componente": "RSI Sobrecomprado",
            "valores": {tf: round(val, 1) for tf, val in rsi_values.items()},
            "pontuacao": analise["pontuacao"],
            "pontuacao_maxima": analise["pontuacao_maxima"],
            "alertas": analise["alertas"],
            "racional": analise["racional"]
        }
    except Exception as e:
        # Em caso de erro, retornar um objeto com pontuação zero, mas bem estruturado
        return {
            "componente": "RSI Sobrecomprado",
            "valores": {},
            "pontuacao": 0.0,
            "pontuacao_maxima": 5.0,
            "alertas": ["Erro ao calcular risco de RSI: " + str(e)],
            "racional": "Erro na obtenção de dados"
        }