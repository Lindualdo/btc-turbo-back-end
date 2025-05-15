import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from app.utils.rsi_utils import calcular_rsi

def identificar_pontos_extremos(serie: pd.Series, janela: int = 3) -> pd.Series:
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

def detectar_divergencias(df: pd.DataFrame, janela_extremos: int = 3, janela_analise: int = 120) -> Dict[str, Any]:
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
    
    # Obter pontos de extremos locais significativos 
    df_topos = df_analise[df_analise['extremos_preco'] == 1].copy()
    df_fundos = df_analise[df_analise['extremos_preco'] == -1].copy()
    
    # Verificar se temos pelo menos dois pontos extremos para comparar
    divergencia_alta = False
    divergencia_baixa = False
    dados_divergencia_alta = None
    dados_divergencia_baixa = None
    
    # Tentar encontrar divergência bearish (baixa) - topos
    if len(df_topos) >= 2:
        # Ordenar por data crescente e pegar os dois últimos
        df_topos_recentes = df_topos.sort_index().tail(2)
        
        # Acessar os valores de preço e RSI
        preco1 = df_topos_recentes.iloc[0]['close']
        preco2 = df_topos_recentes.iloc[1]['close']
        rsi1 = df_topos_recentes.iloc[0]['RSI']
        rsi2 = df_topos_recentes.iloc[1]['RSI']
        
        # Verificar divergência bearish: preço forma topo MAIS ALTO, RSI forma topo MAIS BAIXO
        if preco2 > preco1 and rsi2 < rsi1:
            divergencia_baixa = True
            dados_divergencia_baixa = {
                'data_topo1': df_topos_recentes.index[0].strftime("%Y-%m-%d %H:%M"),
                'preco_topo1': float(preco1),
                'rsi_topo1': float(rsi1),
                'data_topo2': df_topos_recentes.index[1].strftime("%Y-%m-%d %H:%M"),
                'preco_topo2': float(preco2),
                'rsi_topo2': float(rsi2),
                'delta_preco': f'{((preco2 - preco1) / preco1 * 100):.2f}%',
                'delta_rsi': f'{((rsi2 - rsi1) / rsi1 * 100):.2f}%'
            }
    
    # Tentar encontrar divergência bullish (alta) - fundos
    if len(df_fundos) >= 2:
        # Ordenar por data crescente e pegar os dois últimos
        df_fundos_recentes = df_fundos.sort_index().tail(2)
        
        # Acessar os valores de preço e RSI
        preco1 = df_fundos_recentes.iloc[0]['close']
        preco2 = df_fundos_recentes.iloc[1]['close'] 
        rsi1 = df_fundos_recentes.iloc[0]['RSI']
        rsi2 = df_fundos_recentes.iloc[1]['RSI']
        
        # Verificar divergência bullish: preço forma fundo MAIS BAIXO, RSI forma fundo MAIS ALTO
        if preco2 < preco1 and rsi2 > rsi1:
            divergencia_alta = True
            dados_divergencia_alta = {
                'data_fundo1': df_fundos_recentes.index[0].strftime("%Y-%m-%d %H:%M"),
                'preco_fundo1': float(preco1),
                'rsi_fundo1': float(rsi1),
                'data_fundo2': df_fundos_recentes.index[1].strftime("%Y-%m-%d %H:%M"),
                'preco_fundo2': float(preco2),
                'rsi_fundo2': float(rsi2),
                'delta_preco': f'{((preco2 - preco1) / preco1 * 100):.2f}%',
                'delta_rsi': f'{((rsi2 - rsi1) / rsi1 * 100):.2f}%'
            }
    
    # Determinar qual divergência é a mais recente
    tipo_divergencia = None
    data_divergencia = None
    detalhes_divergencia = None
    
    if divergencia_alta and divergencia_baixa:
        # Comparar as datas do último ponto de cada divergência
        data_alta = pd.to_datetime(dados_divergencia_alta['data_fundo2'])
        data_baixa = pd.to_datetime(dados_divergencia_baixa['data_topo2'])
        
        if data_alta > data_baixa:
            tipo_divergencia = "bullish"
            data_divergencia = dados_divergencia_alta['data_fundo2']
            detalhes_divergencia = dados_divergencia_alta
        else:
            tipo_divergencia = "bearish"
            data_divergencia = dados_divergencia_baixa['data_topo2']
            detalhes_divergencia = dados_divergencia_baixa
    elif divergencia_alta:
        tipo_divergencia = "bullish"
        data_divergencia = dados_divergencia_alta['data_fundo2']
        detalhes_divergencia = dados_divergencia_alta
    elif divergencia_baixa:
        tipo_divergencia = "bearish"
        data_divergencia = dados_divergencia_baixa['data_topo2']
        detalhes_divergencia = dados_divergencia_baixa
    
    # Construir resultado
    resultado = {
        "divergencia_detectada": divergencia_alta or divergencia_baixa,
        "tipo_divergencia": tipo_divergencia,
        "data_divergencia": data_divergencia,
        "detalhes": detalhes_divergencia,
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
            "detalhes": analise.get("detalhes"),
            "pontuacao": round(peso if tipo == "bearish" else 0, 2),
            "peso": peso
        }
    
    # Se não há alertas, criar um padrão
    if not alertas:
        alertas = ["Sem divergências RSI bearish detectadas"]
    
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
    timeframes_divergentes = []
    for tf, data in analise.get("analises", {}).items():
        if data.get("divergencia_detectada", False):
            tipo = data.get("tipo_divergencia", "")
            timeframes_divergentes.append(f"{tf} ({tipo})")
    
    # Calcular a pontuação normalizada (0-10)
    normalized_score = 0
    if analise.get("pontuacao_maxima", 0) > 0:
        normalized_score = analise["pontuacao"] / analise["pontuacao_maxima"] * 10
    
    return {
        "pontuacao": round(analise["pontuacao"], 2),
        "pontuacao_maxima": analise["pontuacao_maxima"],
        "pontuacao_normalizada": round(normalized_score, 1),
        "timeframes_com_divergencia": timeframes_divergentes if timeframes_divergentes else ["Nenhum"],
        "alertas": analise.get("alertas", []),
        "racional": analise.get("racional", "")
    }