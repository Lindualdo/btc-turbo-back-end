import logging
from tvDatafeed import TvDatafeed, Interval
import pandas as pd

def get_m2_global_momentum(tv: TvDatafeed):
    """
    Calcula o momentum do M2 Global usando dados reais do TradingView
    
    Returns:
        float: Valor do momentum entre -5 e 5 aproximadamente
    """
    try:
        # Primeiro, tentar acessar o indicador customizado diretamente
        momentum = _try_custom_indicator(tv)
        if momentum is not None:
            return momentum
            
        # Fallback: usar dados econômicos base
        logging.info("Indicador customizado não encontrado, usando dados base...")
        return _calculate_from_base_data(tv)
        
    except Exception as e:
        logging.error(f"Erro ao calcular M2 Global Momentum: {str(e)}")
        raise Exception(f"M2 Global indisponível: {str(e)}")

def _try_custom_indicator(tv: TvDatafeed):
    """
    Tenta acessar o indicador customizado do TradingView
    """
    try:
        # Possíveis formas de acessar o indicador customizado
        custom_symbols = [
            "GLOBAL_M2",
            "WORLD_M2", 
            "GLM2",
            "ECONOMICS:GLOBAL_M2"
        ]
        
        for symbol in custom_symbols:
            try:
                logging.info(f"Tentando acessar {symbol}...")
                df = tv.get_hist(
                    symbol=symbol, 
                    exchange="ECONOMICS", 
                    interval=Interval.in_monthly, 
                    n_bars=24  # 2 anos de dados mensais
                )
                
                if df is not None and not df.empty and len(df) >= 12:
                    return _calculate_momentum(df)
                    
            except Exception as e:
                logging.debug(f"Símbolo {symbol} não encontrado: {str(e)}")
                continue
                
        return None
        
    except Exception as e:
        logging.error(f"Erro ao tentar indicador customizado: {str(e)}")
        return None

def _calculate_from_base_data(tv: TvDatafeed):
    """
    Calcula M2 Global usando dados econômicos base
    Replica a lógica do indicador Pine Script
    """
    try:
        # Principais economias para M2 Global
        m2_sources = [
            ("USM2", "ECONOMICS"),      # EUA - maior peso
            ("CNM2", "ECONOMICS"),      # China - segundo maior
            ("EUM2", "ECONOMICS"),      # Eurozona
            ("JPM2", "ECONOMICS"),      # Japão
        ]
        
        # Taxas de câmbio correspondentes
        fx_rates = [
            ("CNYUSD", "FX_IDC"),       # Para converter CNM2
            ("EURUSD", "FX"),           # Para converter EUM2  
            ("JPYUSD", "FX_IDC"),       # Para converter JPM2
        ]
        
        m2_total_current = 0
        m2_total_12m_ago = 0
        
        # 1. Coletar M2 dos EUA (já em USD)
        us_m2 = tv.get_hist("USM2", "ECONOMICS", Interval.in_monthly, n_bars=13)
        if us_m2 is not None and not us_m2.empty:
            m2_total_current += us_m2.iloc[-1]["close"]
            m2_total_12m_ago += us_m2.iloc[0]["close"] if len(us_m2) >= 13 else us_m2.iloc[-1]["close"]
        
        # 2. Coletar M2 da China e converter para USD
        cn_m2 = tv.get_hist("CNM2", "ECONOMICS", Interval.in_monthly, n_bars=13)
        cny_usd = tv.get_hist("CNYUSD", "FX_IDC", Interval.in_monthly, n_bars=13)
        
        if cn_m2 is not None and cny_usd is not None and not cn_m2.empty and not cny_usd.empty:
            cn_m2_usd_current = cn_m2.iloc[-1]["close"] * cny_usd.iloc[-1]["close"]
            cn_m2_usd_12m = cn_m2.iloc[0]["close"] * cny_usd.iloc[0]["close"] if len(cn_m2) >= 13 else cn_m2_usd_current
            
            m2_total_current += cn_m2_usd_current
            m2_total_12m_ago += cn_m2_usd_12m
        
        # 3. Eurozona
        eu_m2 = tv.get_hist("EUM2", "ECONOMICS", Interval.in_monthly, n_bars=13)
        eur_usd = tv.get_hist("EURUSD", "FX", Interval.in_monthly, n_bars=13)
        
        if eu_m2 is not None and eur_usd is not None and not eu_m2.empty and not eur_usd.empty:
            eu_m2_usd_current = eu_m2.iloc[-1]["close"] * eur_usd.iloc[-1]["close"]
            eu_m2_usd_12m = eu_m2.iloc[0]["close"] * eur_usd.iloc[0]["close"] if len(eu_m2) >= 13 else eu_m2_usd_current
            
            m2_total_current += eu_m2_usd_current
            m2_total_12m_ago += eu_m2_usd_12m
        
        # 4. Japão
        jp_m2 = tv.get_hist("JPM2", "ECONOMICS", Interval.in_monthly, n_bars=13)
        jpy_usd = tv.get_hist("JPYUSD", "FX_IDC", Interval.in_monthly, n_bars=13)
        
        if jp_m2 is not None and jpy_usd is not None and not jp_m2.empty and not jpy_usd.empty:
            jp_m2_usd_current = jp_m2.iloc[-1]["close"] * jpy_usd.iloc[-1]["close"]
            jp_m2_usd_12m = jp_m2.iloc[0]["close"] * jpy_usd.iloc[0]["close"] if len(jp_m2) >= 13 else jp_m2_usd_current
            
            m2_total_current += jp_m2_usd_current
            m2_total_12m_ago += jp_m2_usd_12m
        
        # Calcular crescimento YoY
        if m2_total_12m_ago > 0:
            yoy_growth = ((m2_total_current - m2_total_12m_ago) / m2_total_12m_ago) * 100
            
            # Simular momentum (velocidade de mudança)
            # Por simplicidade, usar o crescimento YoY como proxy
            momentum = yoy_growth
            
            logging.info(f"M2 Global YoY Growth: {yoy_growth:.2f}%")
            return momentum
        else:
            raise Exception("Dados insuficientes para calcular M2 Global")
            
    except Exception as e:
        logging.error(f"Erro ao calcular M2 de dados base: {str(e)}")
        raise Exception(f"Erro nos dados econômicos base: {str(e)}")

def _calculate_momentum(df):
    """
    Calcula momentum a partir de dataframe de M2 Global
    """
    try:
        if len(df) < 12:
            raise Exception("Dados insuficientes para momentum")
            
        # Valor atual e 12 meses atrás
        current_value = df.iloc[-1]["close"]
        value_12m_ago = df.iloc[-12]["close"]
        
        # Crescimento YoY
        yoy_growth = ((current_value - value_12m_ago) / value_12m_ago) * 100
        
        # Momentum = crescimento + aceleração (se tiver dados suficientes)
        momentum = yoy_growth
        
        if len(df) >= 24:
            # Crescimento dos 12 meses anteriores
            value_24m_ago = df.iloc[-24]["close"]
            value_12m_ago_prev = df.iloc[-12]["close"]
            
            prev_yoy_growth = ((value_12m_ago_prev - value_24m_ago) / value_24m_ago) * 100
            
            # Aceleração
            acceleration = yoy_growth - prev_yoy_growth
            momentum = yoy_growth + (acceleration * 0.5)  # Peso para aceleração
        
        logging.info(f"M2 Momentum calculado: {momentum:.2f}%")
        return momentum
        
    except Exception as e:
        logging.error(f"Erro ao calcular momentum: {str(e)}")
        raise Exception(f"Erro no cálculo de momentum: {str(e)}")

def get_m2_global_for_testing():
    """
    Função para testes - retorna valor simulado se APIs falharem
    """
    import random
    return random.uniform(-2, 4)