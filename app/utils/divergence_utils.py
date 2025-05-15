import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from app.utils.rsi_utils import calcular_rsi

def identificar_pontos_extremos(serie: pd.Series, janela: int = 5) -> pd.Series:
    """
    Identifica pontos de máximos e mínimos locais em uma série
    
    Args:
        serie: Série temporal a ser analisada
        janela: Tamanho da janela para buscar extremos locais
        
    Returns:
        Série com valores 1 (máximo local), -1 (mínimo local) ou 0
    """
    extremos = pd.Series(0, index=serie.index)
    
    # Ignorar os primeiros e últimos dados da janela
    for i in range(janela, len(serie) - janela):
        # Verificar se é um ponto de máximo local
        if serie.iloc[i] == max(serie.iloc[i-janela:i+janela+1]):
            extremos.iloc[i] = 1
        # Verificar se é um ponto de mínimo local
        elif serie.iloc[i] == min(serie.iloc[i-janela:i+janela+1]):
            extremos.iloc[i] = -1
            
    return extremos

def detectar_divergencias(df: pd.DataFrame, janela_extremos: int = 5, janela_analise: int = 60) -> Dict[str, Any]:
    """
    Detecta divergências entre preço e RSI
    
    Args:
        df: DataFrame com dados OHLCV e RSI calculado
        janela_extremos: Janela para identificar pontos extremos
        janela_analise: Janela para analisar divergências
        
    Returns:
        Dict com análise de divergências
    """
    # Garantir que temos RSI calculado
    if 'RSI' not in df.columns:
        df = calcular_rsi(df)
        
    # Limitar a janela de análise aos dados mais recentes
    df_analise = df.tail(janela_analise).copy()
    
    # Identificar extremos de preço e RSI
    df_analise['extremos_preco'] = identificar_pontos_extremos(df_analise['close'], janela_extremos)
    df_analise['extremos_rsi'] = identificar_pontos_extremos(df_analise['RSI'], janela_extremos)
    
    # Filtrar apenas pontos com extremos
    df_maximos = df_analise[df_analise['extremos_preco'] == 1].copy()
    df_minimos = df_analise[df_analise['extremos_preco'] == -1].copy()
    
    # Detectar divergência de alta (preço fazendo mínimos mais baixos, RSI fazendo mínimos mais altos)
    divergencia_alta = False
    if len(df_minimos) >= 2:
        # Comparar os dois últimos mínimos
        ultimos_minimos = df_minimos.tail(2)
        if ultimos_minimos.iloc[0]['close'] > ultimos_minimos.iloc[1]['close'] and ultimos_minimos.iloc[0]['RSI'] < ultimos_minimos.iloc[1]['RSI']:
            divergencia_alta = True
            
    # Detectar divergência de baixa (preço fazendo máximos mais altos, RSI fazendo máximos mais baixos)
    divergencia_baixa = False
    if len(df_maximos) >= 2:
        # Comparar os dois últimos máximos
        ultimos_maximos = df_maximos.tail(2)
        if ultimos_maximos.iloc[0]['close'] < ultimos_maximos.iloc[1]['close'] and ultimos_maximos.iloc[0]['RSI'] > ultimos_maximos.iloc[1]['RSI']:
            divergencia_baixa = True
    
    # Verificar a divergência mais recente
    divergencia = None
    tipo_divergencia = None
    data_divergencia = None
    
    if divergencia_alta or divergencia_baixa:
        if divergencia_alta and divergencia_baixa:
            # Se ambas existem, pegar a mais recente
            ultimo_minimo = df_minimos.index[-1] if len(df_minimos) > 0 else pd.Timestamp.min
            ultimo_maximo = df_maximos.index[-1] if len(df_maximos) > 0 else pd.Timestamp.min
            
            if ultimo_minimo > ultimo_maximo:
                divergencia = "alta"
                tipo_divergencia = "bullish"
                data_divergencia = ultimo_minimo
            else:
                divergencia = "baixa"
                tipo_divergencia = "bearish"
                data_divergencia = ultimo_maximo
        elif divergencia_alta:
            divergencia = "alta"
            tipo_divergencia = "bullish"
            data_divergencia = df_minimos.index[-1] if len(df_minimos) > 0 else None
        else:
            divergencia = "baixa"
            tipo_divergencia = "bearish"
            data_divergencia = df_maximos.index[-1] if len(df_maximos) > 0 else None
    
    # Construir resultado
    resultado = {
        "divergencia_detectada": divergencia is not None,
        "tipo_divergencia": tipo_divergencia,
        "data_divergencia": data_divergencia.strftime("%Y-%m-%d %H:%M") if data_divergencia else None,
        "divergencia_alta": divergencia_alta,
        "divergencia_baixa": divergencia_baixa,
        "candles_analisados": len(df_analise)
    }
    
    return resultado

def analisar_divergencias_rsi_risco(divergencias: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analisa o risco com base nas divergências de RSI nos diferentes timeframes
    
    Args:
        divergencias: Dicionário com análise de divergências por timeframe
        
    Returns:
        Dict com análise de risco baseada em divergências
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
    
    for tf, analise in divergencias.items():
        if tf not in pesos or not analise.get("divergencia_detectada", False):
            continue
            
        tipo = analise.get("tipo_divergencia")
        peso = pesos[tf]
        max_pontuacao += peso
        
        # Calcular pontuação - apenas divergências bearish (baixa) representam risco
        if tipo == "bearish":
            pontuacao += peso
            alertas.append(f"Divergência bearish no RSI detectada no {tf}")
            racional.append(f"{tf}: Divergência bearish = {peso} pontos")
        else:
            racional.append(f"{tf}: Divergência bullish = 0 pontos (não representa risco)")
        
        # Armazenar análise por timeframe
        analises[tf] = {
            "divergencia_detectada": analise.get("divergencia_detectada"),
            "tipo_divergencia": tipo,
            "data_divergencia": analise.get("data_divergencia"),
            "pontuacao": peso if tipo == "bearish" else 0,
            "peso": peso
        }
    
    # Se não há alertas, criar um padrão
    if not alertas:
        alertas = ["Sem divergências RSI detectadas"]
    
    return {
        "pontuacao": round(pontuacao, 2),
        "pontuacao_maxima": round(max_pontuacao, 2),
        "analises": analises,
        "racional": ", ".join(racional),
        "alertas": alertas
    }

def consolidar_analise_divergencias(divergencias: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Consolida a análise de risco de divergências RSI
    
    Args:
        divergencias: Dicionário com análises por timeframe
        
    Returns:
        Análise concisa consolidada
    """
    analise = analisar_divergencias_rsi_risco(divergencias)
    
    # Listar timeframes com divergências
    timeframes_divergentes = [
        f"{tf} ({data['tipo_divergencia']})" 
        for tf, data in analise["analises"].items()
    ]
    
    # Calcular a pontuação média normalizada (0-10)
    normalized_score = 0
    
    if analise["pontuacao_maxima"] > 0:
        normalized_score = analise["pontuacao"] / analise["pontuacao_maxima"] * 10
    
    return {
        "pontuacao": round(analise["pontuacao"], 2),
        "pontuacao_maxima": analise["pontuacao_maxima"],
        "pontuacao_normalizada": round(normalized_score, 1),
        "timeframes_com_divergencia": timeframes_divergentes if timeframes_divergentes else ["Nenhum"],
        "alertas": analise["alertas"],
        "racional": analise["racional"]
    }