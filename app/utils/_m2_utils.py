import logging
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
from app.services.tv_session_manager import get_tv_instance

def get_m2_global_momentum():
    """
    Calcula o momentum do M2 Global usando dados reais do TradingView
    Segue o padrão do projeto - usa get_tv_instance() internamente
    
    Returns:
        float: Valor do momentum entre -5 e 5 aproximadamente
    """
    try:
        # Usar o gerenciador de sessão do projeto
        tv = get_tv_instance()
        
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
    Estratégia: Tentar múltiplas exchanges para cada símbolo
    """
    try:
        logging.info("Coletando dados M2 das principais economias...")
        
        m2_data_points = []
        success_count = 0
        
        # Lista de símbolos M2 para tentar, com exchanges alternativas
        m2_symbols = [
            ("USM2", ["ECONOMICS", "FRED"]),
            ("CNM2", ["ECONOMICS"]),
            ("EUM2", ["ECONOMICS", "ECB"]),
            ("JPM2", ["ECONOMICS"]),
            ("GBM2", ["ECONOMICS"]),  # Reino Unido
            ("CAM2", ["ECONOMICS"]),  # Canadá
        ]
        
        for symbol, exchanges in m2_symbols:
            for exchange in exchanges:
                try:
                    logging.info(f"Tentando {symbol} na exchange {exchange}...")
                    df = tv.get_hist(symbol, exchange, Interval.in_monthly, n_bars=15)
                    
                    if df is not None and not df.empty and len(df) >= 12:
                        # Debug: verificar estrutura dos dados
                        logging.info(f"Colunas disponíveis: {df.columns.tolist()}")
                        logging.info(f"Últimas linhas:\n{df.tail(2)}")
                        
                        # Verificar se 'close' existe, senão usar outras colunas
                        price_column = None
                        for col in ['close', 'Close', 'value', 'price']:
                            if col in df.columns:
                                price_column = col
                                break
                        
                        if price_column is None:
                            logging.warning(f"Nenhuma coluna de preço encontrada para {symbol}")
                            continue
                            
                        # Calcular crescimento YoY com verificação de tipos
                        try:
                            current = df.iloc[-1][price_column]
                            year_ago = df.iloc[-12][price_column]
                            
                            # Garantir que são números
                            if not isinstance(current, (int, float)) or not isinstance(year_ago, (int, float)):
                                logging.warning(f"Dados não numéricos para {symbol}: current={current}, year_ago={year_ago}")
                                continue
                                
                            if year_ago == 0:
                                logging.warning(f"Valor zero para {symbol} há 12 meses")
                                continue
                                
                            yoy_growth = ((current - year_ago) / year_ago) * 100
                        
                        m2_data_points.append({
                            "symbol": symbol,
                            "exchange": exchange,
                            "yoy_growth": yoy_growth,
                            "current_value": float(current),
                            "column_used": price_column
                        })
                        
                        success_count += 1
                        logging.info(f"✅ {symbol}: {yoy_growth:.2f}% YoY (usando coluna '{price_column}')")
                        break  # Sucesso, não tentar outras exchanges
                        
                        except Exception as calc_error:
                            logging.warning(f"Erro no cálculo para {symbol}: {str(calc_error)}")
                            continue
                        
                except Exception as e:
                    logging.debug(f"Falha {symbol} em {exchange}: {str(e)}")
                    continue
        
        if success_count == 0:
            raise Exception("Nenhum dado M2 coletado com sucesso")
        
        # Calcular momentum ponderado
        # EUA tem maior peso na economia global
        weights = {
            "USM2": 0.4,   # 40% - EUA
            "CNM2": 0.25,  # 25% - China  
            "EUM2": 0.20,  # 20% - Eurozona
            "JPM2": 0.10,  # 10% - Japão
            "GBM2": 0.03,  # 3% - Reino Unido
            "CAM2": 0.02   # 2% - Canadá
        }
        
        weighted_momentum = 0
        total_weight = 0
        
        for data_point in m2_data_points:
            symbol = data_point["symbol"]
            weight = weights.get(symbol, 0.01)  # Peso padrão baixo
            weighted_momentum += data_point["yoy_growth"] * weight
            total_weight += weight
        
        # Normalizar se não temos todos os pesos
        if total_weight > 0:
            final_momentum = weighted_momentum / total_weight
        else:
            # Fallback: média simples
            final_momentum = sum([dp["yoy_growth"] for dp in m2_data_points]) / len(m2_data_points)
        
        logging.info(f"M2 Global Momentum Final: {final_momentum:.2f}% (baseado em {success_count} países)")
        return final_momentum
        
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
    Função para testes e emergência - retorna valor baseado em lógica econômica
    Se todas as APIs falharem, usa estimativa baseada em contexto macro atual
    """
    import random
    import datetime
    
    # Base: contexto macroeconômico de 2025
    # Pós-pandemia, políticas expansivas ainda em vigor
    base_growth = 4.0  # Base: 4% crescimento M2 anual
    
    # Adicionar variação sazonal/mensal realista
    current_month = datetime.datetime.now().month
    seasonal_adjust = 0.5 * (current_month - 6) / 6  # Leve variação sazonal
    
    # Adicionar ruído realista
    noise = random.uniform(-1.5, 1.5)
    
    estimated_momentum = base_growth + seasonal_adjust + noise
    
    logging.warning(f"Usando estimativa M2: {estimated_momentum:.2f}% (todas as APIs falharam)")
    return estimated_momentum

def test_m2_collection():
    """
    Função de teste para verificar se conseguimos coletar dados M2
    """
    try:
        momentum = get_m2_global_momentum()
        logging.info(f"✅ Teste M2 bem-sucedido: {momentum:.2f}%")
        return True, momentum
    except Exception as e:
        logging.error(f"❌ Teste M2 falhado: {str(e)}")
        return False, str(e)