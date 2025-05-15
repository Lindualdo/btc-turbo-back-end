from app.services.tv_session_manager import get_tv_instance
from app.utils.rsi_utils import calcular_rsi
from app.utils.divergence_utils import detectar_divergencias, analisar_divergencias_rsi_risco
from tvDatafeed import Interval
import pandas as pd
from typing import Dict, Any

interval_map = {
    "15m": Interval.in_15_minute,
    "30m": Interval.in_30_minute,
    "1h": Interval.in_1_hour,
    "4h": Interval.in_4_hour,
    "1d": Interval.in_daily,
    "1w": Interval.in_weekly
}

def get_divergence_data() -> Dict[str, Dict[str, Any]]:
    """
    Obtém os dados de divergências RSI de todos os timeframes
    
    Returns:
        Dicionário com análises de divergência por timeframe
    """
    tv = get_tv_instance()
    divergencias = {}
    
    for key, interval in interval_map.items():
        try:
            df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=interval, n_bars=500)
            
            if not isinstance(df, pd.DataFrame) or df.empty:
                continue
                
            # Calcular RSI
            df = calcular_rsi(df, periodo=14)
            
            # Detectar divergências
            divergencias[key] = detectar_divergencias(df)
                
        except Exception:
            # Silently continue if we can't get data for a timeframe
            continue
    
    return divergencias

def calculate_divergence_risk() -> Dict[str, Any]:
    """
    Calcula o componente de risco de divergências RSI para análise de risco técnico
    
    Returns:
        Componente de risco de divergências para a análise técnica
    """
    try:
        # Obter análises de divergência
        divergencias = get_divergence_data()
        
        # Analisar risco com base nas divergências
        analise = analisar_divergencias_rsi_risco(divergencias)
        
        # Formatar resultados para mostrar apenas tfs com divergências
        divergencias_formatadas = {}
        for tf, data in divergencias.items():
            if data.get("divergencia_detectada", False):
                divergencias_formatadas[tf] = {
                    "tipo": data.get("tipo_divergencia", "N/A"),
                    "data": data.get("data_divergencia", "N/A")
                }
        
        return {
            "componente": "Divergências RSI",
            "divergencias_detectadas": divergencias_formatadas,
            "pontuacao": analise["pontuacao"],
            "pontuacao_maxima": analise["pontuacao_maxima"],
            "alertas": analise["alertas"],
            "racional": analise["racional"]
        }
    except Exception as e:
        # Em caso de erro, retornar um objeto com pontuação zero, mas bem estruturado
        return {
            "componente": "Divergências RSI",
            "divergencias_detectadas": {},
            "pontuacao": 0.0,
            "pontuacao_maxima": 5.0,
            "alertas": ["Erro ao calcular risco de divergências RSI: " + str(e)],
            "racional": "Erro na obtenção de dados"
        }