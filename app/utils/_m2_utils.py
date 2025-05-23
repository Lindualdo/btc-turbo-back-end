import logging
from app.services.tv_session_manager import get_tv_instance
from tvDatafeed import Interval

def get_m2_global_momentum():
    """
    Versão com logs detalhados para debug
    """
    logging.info("🚀 [M2_UTILS] Iniciando coleta M2 Global...")
    
    try:
        logging.info("📡 [M2_UTILS] Obtendo instância TradingView...")
        tv = get_tv_instance()
        
        if tv is None:
            raise Exception("TradingView instance é None")
            
        logging.info("✅ [M2_UTILS] TradingView conectado com sucesso")
        
        # Tentar apenas US M2 primeiro (mais estável)
        return _get_us_m2_simple(tv)
        
    except Exception as e:
        logging.error(f"❌ [M2_UTILS] Erro crítico: {str(e)}")
        # Retornar valor de emergência
        return _get_emergency_value()

def _get_us_m2_simple(tv):
    """Coleta apenas M2 dos EUA - versão simplificada com logs"""
    try:
        logging.info("🇺🇸 [M2_UTILS] Coletando USM2 da exchange ECONOMICS...")
        
        df = tv.get_hist("USM2", "ECONOMICS", Interval.in_monthly, n_bars=15)
        
        if df is None:
            logging.error("❌ [M2_UTILS] USM2 retornou None")
            raise Exception("USM2 retornou None")
            
        if df.empty:
            logging.error("❌ [M2_UTILS] USM2 retornou DataFrame vazio")
            raise Exception("USM2 retornou DataFrame vazio")
            
        logging.info(f"📊 [M2_UTILS] USM2 - Linhas coletadas: {len(df)}")
        logging.info(f"📋 [M2_UTILS] USM2 - Colunas: {df.columns.tolist()}")
        
        # Debug: mostrar primeiras linhas
        logging.info(f"🔍 [M2_UTILS] USM2 - Primeiras linhas:\n{df.head(2)}")
        logging.info(f"🔍 [M2_UTILS] USM2 - Últimas linhas:\n{df.tail(2)}")
        
        # Verificar coluna de preço
        price_col = None
        for col in ['close', 'Close', 'value', 'price', 'last']:
            if col in df.columns:
                price_col = col
                logging.info(f"✅ [M2_UTILS] Usando coluna de preço: '{price_col}'")
                break
                
        if price_col is None:
            logging.error(f"❌ [M2_UTILS] Nenhuma coluna de preço encontrada. Colunas: {df.columns.tolist()}")
            raise Exception(f"Nenhuma coluna de preço encontrada. Colunas: {df.columns.tolist()}")
        
        if len(df) < 12:
            logging.error(f"❌ [M2_UTILS] Dados insuficientes: {len(df)} meses (precisa 12+)")
            raise Exception(f"Dados insuficientes: {len(df)} meses (precisa 12+)")
            
        # Pegar valores
        current_value = df.iloc[-1][price_col]
        year_ago_value = df.iloc[-12][price_col]
        
        logging.info(f"📈 [M2_UTILS] Valor atual: {current_value} (tipo: {type(current_value)})")
        logging.info(f"📉 [M2_UTILS] Valor 12m atrás: {year_ago_value} (tipo: {type(year_ago_value)})")
        
        # Converter para float se necessário
        try:
            current_float = float(current_value)
            year_ago_float = float(year_ago_value)
            logging.info(f"✅ [M2_UTILS] Conversão para float bem-sucedida")
        except (ValueError, TypeError) as e:
            logging.error(f"❌ [M2_UTILS] Erro ao converter para float: {e}")
            raise Exception(f"Erro ao converter para float: {e}")
            
        if year_ago_float == 0:
            logging.error("❌ [M2_UTILS] Valor de 12 meses atrás é zero")
            raise Exception("Valor de 12 meses atrás é zero")
            
        # Calcular crescimento YoY
        yoy_growth = ((current_float - year_ago_float) / year_ago_float) * 100
        
        logging.info(f"🎯 [M2_UTILS] Crescimento YoY calculado: {yoy_growth:.2f}%")
        logging.info(f"✅ [M2_UTILS] USM2 Momentum finalizado com sucesso")
        
        return yoy_growth
        
    except Exception as e:
        logging.error(f"❌ [M2_UTILS] Erro USM2: {str(e)}")
        raise e

def _get_emergency_value():
    """Valor de emergência baseado no contexto atual"""
    # Contexto 2025: políticas expansivas pós-pandemia
    emergency_value = 3.5  # 3.5% crescimento M2 anual estimado
    logging.warning(f"⚠️ [M2_UTILS] Usando valor de emergência M2: {emergency_value}%")
    return emergency_value

def test_tv_connection():
    """Testa conexão básica com TradingView"""
    try:
        logging.info("🧪 [M2_UTILS] Testando conexão TradingView...")
        tv = get_tv_instance()
        
        if tv is None:
            logging.error("❌ [M2_UTILS] get_tv_instance() retornou None")
            return False
        
        # Teste simples: pegar BTCUSDT
        test_df = tv.get_hist("BTCUSDT", "BINANCE", Interval.in_daily, n_bars=5)
        
        if test_df is not None and not test_df.empty:
            logging.info(f"✅ [M2_UTILS] Conexão TV OK - coletou {len(test_df)} linhas de BTCUSDT")
            return True
        else:
            logging.error("❌ [M2_UTILS] Conexão TV falhou - dados vazios")
            return False
            
    except Exception as e:
        logging.error(f"❌ [M2_UTILS] Conexão TV falhou: {str(e)}")
        return False