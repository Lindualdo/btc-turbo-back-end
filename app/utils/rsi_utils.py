# app/utils/rsi_utils.py

import pandas as pd
import numpy as np
from typing import Dict, Any, List

def calcular_rsi(df: pd.DataFrame, periodo: int = 14) -> pd.DataFrame:
    """
    Calcula o RSI (Índice de Força Relativa) para um DataFrame de preços
    
    Args:
        df: DataFrame com dados OHLCV
        periodo: Período para cálculo do RSI (padrão: 14)
        
    Returns:
        DataFrame com a coluna RSI adicionada
    """
    # Garantir que temos pelo menos periodo+1 dados
    if len(df) <= periodo:
        return df
    
    # Calcular as mudanças de preços
    delta = df['close'].diff()
    
    # Separar ganhos (up) e perdas (down)
    ganhos = delta.copy()
    perdas = delta.copy()
    ganhos[ganhos < 0] = 0
    perdas[perdas > 0] = 0
    perdas = abs(perdas)
    
    # Calcular médias móveis de ganhos e perdas
    avg_gain = ganhos.rolling(window=periodo).mean()
    avg_loss = perdas.rolling(window=periodo).mean()
    
    # Calcular RS (Relative Strength)
    rs = avg_gain / avg_loss
    
    # Calcular RSI
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df

def analisar_rsi_timeframe(rsi_value: float) -> Dict[str, Any]:
    """
    Analisa o valor do RSI e determina a condição do mercado
    
    Args:
        rsi_value: Valor do RSI
        
    Returns:
        Dict com a análise do RSI
    """
    if rsi_value > 80:
        condition = "Extremamente sobrecomprado"
        risk = "alto"
    elif rsi_value > 70:
        condition = "Sobrecomprado"
        risk = "elevado"
    elif rsi_value > 60:
        condition = "Levemente sobrecomprado"
        risk = "moderado"
    elif rsi_value > 40:
        condition = "Neutro"
        risk = "baixo"
    elif rsi_value > 30:
        condition = "Levemente sobrevendido"
        risk = "baixo"
    elif rsi_value > 20:
        condition = "Sobrevendido"
        risk = "baixo"
    else:
        condition = "Extremamente sobrevendido"
        risk = "baixo"
    
    return {
        "valor": round(rsi_value, 2),
        "condicao": condition,
        "risco": risk
    }

def analisar_rsi_risco(rsi_values: Dict[str, float]) -> Dict[str, Any]:
    """
    Calcula a pontuação de risco com base nos valores do RSI por timeframe
    
    Args:
        rsi_values: Dicionário com valores do RSI por timeframe
        
    Returns:
        Dict com análise de risco baseada no RSI
    """
    # Pesos por timeframe
    pesos = {
        "1w": 2.0,
        "1d": 1.5,
        "4h": 1.0,
        "1h": 0.3,
        "30m": 0.1,
        "15m": 0.1
    }
    
    pontuacao = 0.0
    max_pontuacao = 0.0
    analises = {}
    racional = []
    alertas = []
    
    for tf, peso in pesos.items():
        if tf not in rsi_values:
            continue
            
        rsi = rsi_values[tf]
        max_pontuacao += peso
        
        # Cálculo da pontuação de risco por timeframe
        if rsi > 80:
            tf_score = peso  # Pontuação máxima
            alertas.append(f"IFR extremamente sobrecomprado ({rsi:.1f}) no {tf}")
            racional.append(f"{tf}: {rsi:.1f} > 80 = {peso} pontos")
        elif rsi > 70:
            tf_score = 0.8 * peso
            alertas.append(f"IFR sobrecomprado ({rsi:.1f}) no {tf}")
            racional.append(f"{tf}: {rsi:.1f} > 70 = {0.8 * peso:.2f} pontos")
        elif rsi > 65:
            tf_score = 0.4 * peso
            racional.append(f"{tf}: {rsi:.1f} > 65 = {0.4 * peso:.2f} pontos")
        else:
            tf_score = 0.0
            racional.append(f"{tf}: {rsi:.1f} < 65 = 0 pontos")
        
        pontuacao += tf_score
        
        # Armazenar análise por timeframe
        analises[tf] = {
            "rsi": round(rsi, 1),
            "risco": analisar_rsi_timeframe(rsi),
            "pontuacao": round(tf_score, 2),
            "peso": peso
        }
    
    # Se não há alertas, criar um padrão
    if not alertas:
        alertas = ["Sem alertas de sobrecompra de IFR"]
    
    return {
        "pontuacao": round(pontuacao, 2),
        "pontuacao_maxima": round(max_pontuacao, 2),
        "analises": analises,
        "racional": ", ".join(racional),
        "alertas": alertas
    }

def consolidar_analise_rsi(rsi_values: Dict[str, float]) -> Dict[str, Any]:
    """
    Consolida a análise de risco do RSI
    
    Args:
        rsi_values: Dicionário com valores do RSI por timeframe
        
    Returns:
        Análise concisa consolidada
    """
    analise = analisar_rsi_risco(rsi_values)
    
    # Coletar os timeframes disponíveis
    timeframes_str = ", ".join(list(analise["analises"].keys()))
    
    # Calcular a pontuação média normalizada (0-10)
    normalized_score = analise["pontuacao"] / analise["pontuacao_maxima"] * 10 if analise["pontuacao_maxima"] > 0 else 0
    
    return {
        "pontuacao": round(analise["pontuacao"], 2),
        "pontuacao_maxima": analise["pontuacao_maxima"],
        "pontuacao_normalizada": round(normalized_score, 1),
        "timeframes": timeframes_str,
        "valores_por_timeframe": {
            tf: data["rsi"] for tf, data in analise["analises"].items()
        },
        "alertas": analise["alertas"],
        "racional": analise["racional"]
    }