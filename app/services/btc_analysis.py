import os
from tvDatafeed import TvDatafeed, Interval
import requests
from app.config import get_settings
import logging
from app.utils.m2_utils import get_m2_global_momentum


def get_btc_vs_200d_ema(tv: TvDatafeed):
    """
    Analisa a força do bull market baseado na posição do BTC vs EMA 200D
    Retorna score de 0-10 com classificação em 5 níveis
    """
    try:
        df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=Interval.in_daily, n_bars=250)
        df["EMA_200"] = df["close"].ewm(span=200, adjust=False).mean()
        latest = df.iloc[-1]
        close = latest["close"]
        ema200 = df["EMA_200"].iloc[-1]
        variacao_pct = ((close - ema200) / ema200) * 100

        # Classificar força do bull market
        score, classificacao = _classify_bull_market_strength(variacao_pct)

        return {
            "indicador": "BTC vs EMA 200D",
            "fonte": "TradingView",
            "valor_coletado": f"BTC {variacao_pct:.1f}% vs EMA 200D",
            "score": score,
            f"score_ponderado ({score} × 0.30)": score * 0.30,
            "classificacao": classificacao,
            "observação": "Força do bull market baseada na distância do preço atual vs EMA 200 dias",
            "detalhes": {
                "preco_atual": round(close, 2),
                "ema_200": round(ema200, 2),
                "variacao_percentual": round(variacao_pct, 2)
            }
        }

    except Exception as e:
        return {
            "indicador": "BTC vs EMA 200D",
            "fonte": "TradingView",
            "valor_coletado": "erro",
            "score": 0.0,
            f"score_ponderado (0.0 × 0.30)": 0.0,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro: {str(e)}",
            "detalhes": {
                "preco_atual": None,
                "ema_200": None,
                "variacao_percentual": None
            }
        }


def _classify_bull_market_strength(variacao_pct):
    """
    Classifica a força do bull market baseado na variação percentual vs EMA 200D
    """
    if variacao_pct > 30:
        return 9.0, "Bull Parabólico"
    elif variacao_pct > 15:
        return 7.0, "Bull Forte"  
    elif variacao_pct > 5:
        return 5.0, "Bull Moderado"
    elif variacao_pct > 0:
        return 3.0, "Bull Inicial"
    else:
        return 1.0, "Bull Não Confirmado"


def get_btc_vs_realized_price(tv: TvDatafeed):
    """
    Analisa a fase do ciclo baseado na posição do BTC vs Realized Price
    Retorna score de 0-10 com classificação em 5 níveis
    Agora usa dados reais do TradingView via MVRV
    """
    try:
        # Buscar preço atual do BTC
        df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=Interval.in_daily, n_bars=1)
        preco_atual = df.iloc[-1]["close"]
        
        # Buscar Realized Price via TradingView (usando MVRV)
        realized_price, fonte_dados = _get_realized_price_from_tv(tv, preco_atual)
        
        # Se não encontrou dados válidos, retornar erro
        if realized_price == 0:
            return {
                "indicador": "BTC vs Realized Price",
                "fonte": fonte_dados,
                "valor_coletado": "erro - dados não encontrados",
                "score": 0.0,
                f"score_ponderado (0.0 × 0.30)": 0.0,
                "classificacao": "Dados indisponíveis",
                "observação": "Não foi possível obter Realized Price do TradingView",
                "detalhes": {
                    "preco_atual": round(preco_atual, 2),
                    "realized_price": 0,
                    "variacao_percentual": 0,
                    "metodo_calculo": "Erro - sem dados"
                }
            }
        
        variacao_pct = ((preco_atual - realized_price) / realized_price) * 100

        # Classificar fase do ciclo
        score, classificacao = _classify_cycle_phase(variacao_pct)

        return {
            "indicador": "BTC vs Realized Price",
            "fonte": fonte_dados,
            "valor_coletado": f"BTC {variacao_pct:.1f}% vs Realized Price",
            "score": score,
            f"score_ponderado ({score} × 0.30)": score * 0.30,
            "classificacao": classificacao,
            "observação": "Compara preço de mercado com preço médio pago pelos holders para avaliar fase do ciclo",
            "detalhes": {
                "preco_atual": round(preco_atual, 2),
                "realized_price": round(realized_price, 2),
                "variacao_percentual": round(variacao_pct, 2),
                "metodo_calculo": "TradingView MVRV" if "TradingView" in fonte_dados else "Erro"
            }
        }

    except Exception as e:
        return {
            "indicador": "BTC vs Realized Price",
            "fonte": "Erro",
            "valor_coletado": "erro",
            "score": 0.0,
            f"score_ponderado (0.0 × 0.30)": 0.0,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro: {str(e)}",
            "detalhes": {
                "preco_atual": None,
                "realized_price": None,
                "variacao_percentual": None,
                "metodo_calculo": "Erro"
            }
        }


def _get_realized_price_from_tv(tv, current_btc_price):
    """
    Busca Realized Price via TradingView usando múltiplas estratégias
    Prioridade: MVRV > Market Cap/Supply
    Retorna 0 se não encontrar dados válidos
    """
    try:
        # Estratégia 1: Usar MVRV Ratio
        logging.info("📊 Tentando calcular Realized Price via MVRV...")
        
        # Tentar diferentes símbolos MVRV
        mvrv_symbols = [
            ("BTC_MVRV", "ECONOMICS"),
            ("MVRV", "CRYPTO"),
            ("BTC.MVRV", "INDEX"),
            ("BTCMVRV", "ECONOMICS")
        ]
        
        for symbol, exchange in mvrv_symbols:
            try:
                logging.info(f"🔍 Tentando {symbol} na exchange {exchange}...")
                mvrv_df = tv.get_hist(symbol, exchange, Interval.in_daily, n_bars=5)
                
                if mvrv_df is not None and not mvrv_df.empty:
                    mvrv_ratio = mvrv_df.iloc[-1]["close"]
                    
                    # Validar MVRV (deve estar entre 0.5 e 10 normalmente)
                    if 0.5 <= mvrv_ratio <= 10:
                        realized_price = current_btc_price / mvrv_ratio
                        logging.info(f"✅ MVRV encontrado: {mvrv_ratio:.2f}, Realized Price: ${realized_price:.0f}")
                        return realized_price, f"TradingView MVRV ({exchange})"
                    else:
                        logging.warning(f"⚠️ MVRV inválido: {mvrv_ratio}")
                        
            except Exception as e:
                logging.debug(f"❌ {symbol} falhou: {str(e)}")
                continue
        
        # Estratégia 2: Usar Market Cap / Supply
        logging.info("📊 Tentando calcular via Market Cap / Supply...")
        try:
            cap_symbols = [
                ("BTC_MARKET_CAP", "ECONOMICS"),
                ("BTCUSD_MARKET_CAP", "CRYPTO"),
                ("BTC.MCAP", "INDEX")
            ]
            
            supply_symbols = [
                ("BTC_SUPPLY", "ECONOMICS"),
                ("BTC_CIRCULATING_SUPPLY", "CRYPTO"),
                ("BTC.SUPPLY", "INDEX")
            ]
            
            market_cap = None
            supply = None
            
            # Buscar Market Cap
            for symbol, exchange in cap_symbols:
                try:
                    df = tv.get_hist(symbol, exchange, Interval.in_daily, n_bars=1)
                    if df is not None and not df.empty:
                        market_cap = df.iloc[-1]["close"]
                        break
                except:
                    continue
            
            # Buscar Supply
            for symbol, exchange in supply_symbols:
                try:
                    df = tv.get_hist(symbol, exchange, Interval.in_daily, n_bars=1)
                    if df is not None and not df.empty:
                        supply = df.iloc[-1]["close"]
                        break
                except:
                    continue
            
            if market_cap and supply and supply > 0:
                realized_price = market_cap / supply
                if 20000 <= realized_price <= 100000:  # Sanity check
                    logging.info(f"✅ Market Cap/Supply calculado: ${realized_price:.0f}")
                    return realized_price, "TradingView Market Cap/Supply"
                    
        except Exception as e:
            logging.debug(f"❌ Market Cap/Supply falhou: {str(e)}")
        
        # Se chegou aqui, não encontrou dados válidos
        logging.error("❌ Nenhuma estratégia funcionou para Realized Price")
        return 0, "Erro - Dados não encontrados no TradingView"
        
    except Exception as e:
        logging.error(f"❌ Erro crítico ao buscar Realized Price: {str(e)}")
        return 0, f"Erro - {str(e)}"


def _classify_cycle_phase(variacao_pct):
    """
    Classifica a fase do ciclo baseado na variação vs Realized Price
    """
    if variacao_pct > 50:
        return 9.0, "Ciclo Aquecido"
    elif variacao_pct > 20:
        return 7.0, "Ciclo Normal"
    elif variacao_pct > -10:
        return 5.0, "Acumulação"
    elif variacao_pct > -30:
        return 3.0, "Capitulação Leve"
    else:
        return 1.0, "Capitulação Severa"


def get_puell_multiple():
    """
    Analisa a pressão dos mineradores baseado no Puell Multiple
    Retorna score de 0-10 com classificação em 5 níveis
    """
    try:
        from notion_client import Client
        settings = get_settings()
        NOTION_TOKEN = settings.NOTION_TOKEN
        
        DATABASE_ID = settings.NOTION_DATABASE_ID_MACRO.strip().replace('"', '')
        
        if not DATABASE_ID:
            raise ValueError("DATABASE_ID não pode ser vazio.")
            
        notion = Client(auth=NOTION_TOKEN)
        response = notion.databases.query(database_id=DATABASE_ID)
        
        for row in response["results"]:
            props = row["properties"]
            nome = props["indicador"]["title"][0]["plain_text"].strip().lower()
            if nome == "puell_multiple":
                valor = float(props["valor"]["number"])
                
                # Classificar pressão dos mineradores
                score, classificacao = _classify_miner_pressure(valor)

                return {
                    "indicador": "Puell Multiple",
                    "fonte": "Notion API / Glassnode",
                    "valor_coletado": f"{valor:.2f}",
                    "score": score,
                    f"score_ponderado ({score} × 0.20)": score * 0.20,
                    "classificacao": classificacao,
                    "observação": "Ratio da receita diária dos mineradores vs média de 1 ano - indica pressão de venda",
                    "detalhes": {
                        "puell_value": valor
                    }
                }

        raise ValueError("Indicador 'puell_multiple' não encontrado.")
        
    except Exception as e:
        return {
            "indicador": "Puell Multiple",
            "fonte": "Notion API / Glassnode",
            "valor_coletado": "erro",
            "score": 0.0,
            f"score_ponderado (0.0 × 0.20)": 0.0,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro: {str(e)}",
            "detalhes": {
                "puell_value": None
            }
        }


def _classify_miner_pressure(puell_value):
    """
    Classifica a pressão dos mineradores baseado no Puell Multiple
    """
    if 0.5 <= puell_value <= 1.2:
        return 9.0, "Zona Ideal"
    elif 1.2 < puell_value <= 1.8:
        return 7.0, "Leve Aquecimento"
    elif (0.3 <= puell_value < 0.5) or (1.8 < puell_value <= 2.5):
        return 5.0, "Neutro"
    elif 2.5 < puell_value <= 4.0:
        return 3.0, "Tensão Alta"
    else:
        return 1.0, "Extremo"


def get_funding_rates_analysis():
    """
    Analisa o sentimento do mercado baseado nas Funding Rates
    Retorna score de 0-10 com classificação em 5 níveis
    """
    try:
        url = "https://fapi.binance.com/fapi/v1/fundingRate"
        params = {"symbol": "BTCUSDT", "limit": 56}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data:
            rates = [float(item["fundingRate"]) * 100 for item in data]
            avg_7d = sum(rates) / len(rates)
        else:
            avg_7d = 0.05
            
        # Classificar sentimento do mercado
        score, classificacao = _classify_market_sentiment(avg_7d)
        
        return {
            "indicador": "Funding Rates 7D Média",
            "fonte": "Binance API",
            "valor_coletado": f"{avg_7d:.3f}%",
            "score": score,
            f"score_ponderado ({score} × 0.05)": score * 0.05,
            "classificacao": classificacao,
            "observação": "Média de 7 dias das taxas de funding dos contratos perpétuos - indica sentimento do mercado",
            "detalhes": {
                "funding_rate_7d": round(avg_7d, 4)
            }
        }
        
    except Exception as e:
        return {
            "indicador": "Funding Rates 7D Média",
            "fonte": "Binance API",
            "valor_coletado": "erro",
            "score": 0.0,
            f"score_ponderado (0.0 × 0.05)": 0.0,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro: {str(e)}",
            "detalhes": {
                "funding_rate_7d": None
            }
        }


def _classify_market_sentiment(avg_7d):
    """
    Classifica o sentimento do mercado baseado nas Funding Rates
    """
    if 0 <= avg_7d <= 0.1:
        return 9.0, "Sentimento Equilibrado"
    elif 0.1 < avg_7d <= 0.2:
        return 7.0, "Otimismo Moderado"
    elif 0.2 < avg_7d <= 0.3:
        return 5.0, "Aquecimento"
    elif 0.3 < avg_7d <= 0.5:
        return 3.0, "Euforia Inicial"
    else:
        return 1.0, "Euforia Extrema"


def get_m2_global_momentum():
    """M2 Global Momentum Score - APIs primeiro, Notion como fallback"""
    try:
        logging.info("🚀 Iniciando coleta M2 Global Momentum...")
        
        # Tentar APIs dos bancos centrais primeiro
        try:
            logging.info("📊 Tentando coletar dados M2 via TradingView...")
            momentum_value = _get_m2_from_apis()
            fonte = "TradingView APIs"
            logging.info(f"✅ M2 coletado com sucesso: {momentum_value:.2f}%")
        except Exception as api_error:
            logging.warning(f"⚠️ APIs TradingView falharam: {str(api_error)}")
            # Fallback para Notion
            logging.info("📝 Tentando fallback via Notion...")
            momentum_value = _get_m2_from_notion()
            fonte = "Notion API"
            logging.info(f"✅ M2 via Notion: {momentum_value:.2f}%")
        
        # Classificar momentum
        logging.info(f"🧮 Classificando momentum: {momentum_value:.2f}%")
        
        if momentum_value > 3:
            score = 9.0
            classificacao = "Aceleração Forte"
        elif momentum_value > 1:
            score = 7.0
            classificacao = "Aceleração Moderada"
        elif momentum_value > -1:
            score = 5.0
            classificacao = "Estável"
        elif momentum_value > -3:
            score = 3.0
            classificacao = "Desaceleração"
        else:
            score = 1.0
            classificacao = "Contração"
            
        resultado = {
            "indicador": "M2 Global Momentum",
            "fonte": fonte,
            "valor_coletado": f"{momentum_value:.1f}% momentum",
            "score": score,
            f"score_ponderado ({score} × 0.15)": score * 0.15,
            "classificacao": classificacao,
            "observação": "Velocidade de mudança na expansão monetária global - indica aceleração ou desaceleração de liquidez"
        }
        
        logging.info(f"✅ M2 Global finalizado - Score: {score}, Classificação: {classificacao}")
        return resultado
        
    except Exception as e:
        logging.error(f"❌ Erro crítico M2 Global: {str(e)}")
        return {
            "indicador": "M2 Global Momentum", 
            "fonte": "Erro",
            "valor_coletado": "erro",
            "score": 5.0,  # Neutro em caso de erro
            f"score_ponderado (5.0 × 0.15)": 5.0 * 0.15,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro: {str(e)}"
        }


def _get_m2_from_apis():
    """Busca M2 das APIs dos bancos centrais - VERSÃO CORRIGIDA SEM RECURSÃO"""
    try:
        logging.info("🔧 Iniciando coleta M2 via utilitário...")
        
        # IMPORTANTE: Importar aqui para evitar recursão
        from app.utils.m2_utils import get_m2_global_momentum as m2_utils_function
        
        # Usar o utilitário que já gerencia a sessão TradingView internamente
        momentum_value = m2_utils_function()
        
        logging.info(f"📈 M2 coletado via utils: {momentum_value:.2f}%")
        return momentum_value
        
    except Exception as e:
        logging.error(f"❌ Erro ao buscar M2 via utils: {str(e)}")
        raise Exception(f"APIs M2 indisponíveis: {str(e)}")


def _get_m2_from_notion():
    """Busca M2 do Notion como fallback - COM LOGS"""
    try:
        logging.info("📝 Buscando M2 no Notion...")
        
        from notion_client import Client
        settings = get_settings()
        notion = Client(auth=settings.NOTION_TOKEN)
        DATABASE_ID = settings.NOTION_DATABASE_ID_MACRO.strip().replace('"', '')
        
        logging.info(f"🔍 Consultando Notion DB: {DATABASE_ID}")
        response = notion.databases.query(database_id=DATABASE_ID)
        
        logging.info(f"📊 Encontrados {len(response['results'])} registros no Notion")
        
        for row in response["results"]:
            props = row["properties"]
            nome = props["indicador"]["title"][0]["plain_text"].strip().lower()
            logging.info(f"🔍 Verificando indicador: '{nome}'")
            
            if nome in ["m2_global", "m2_momentum", "expansao_global"]:
                valor = float(props["valor"]["number"])
                logging.info(f"✅ Encontrado {nome}: {valor}")
                return valor
                
        # Se não encontrar, usar expansão global como proxy
        logging.warning("⚠️ M2 específico não encontrado, usando valor padrão")
        return 2.0  # Valor neutro default
        
    except Exception as e:
        logging.error(f"❌ Erro Notion M2: {str(e)}")
        raise Exception(f"Erro Notion M2: {str(e)}")


# FUNÇÃO PRINCIPAL - LIMPA E ORGANIZADA
def analyze_btc_cycles_v2(tv):
    """
    Análise de ciclos BTC v2.0 - VERSÃO FINAL LIMPA
    Usa diretamente as funções refatoradas - sem duplicação de lógica
    """
    try:
        indicadores = []
        
        # 1. BTC vs EMA 200D (30%)
        btc_ema_data = get_btc_vs_200d_ema(tv)
        indicadores.append(btc_ema_data)
        
        # 2. BTC vs Realized Price (30%)
        realized_data = get_btc_vs_realized_price(tv)
        indicadores.append(realized_data)
        
        # 3. Puell Multiple (20%)
        puell_data = get_puell_multiple()
        indicadores.append(puell_data)
        
        # 4. M2 Global Momentum (15%)
        m2_data = get_m2_global_momentum()
        indicadores.append(m2_data)
        
        # 5. Funding Rates 7D (5%)
        funding_data = get_funding_rates_analysis()
        indicadores.append(funding_data)
        
        # Calcular score consolidado - busca pela chave que contém "score_ponderado"
        score_consolidado = 0
        for ind in indicadores:
            for key, value in ind.items():
                if "score_ponderado" in key and isinstance(value, (int, float)):
                    score_consolidado += value
                    break
        
        # Classificação final
        if score_consolidado >= 8.1:
            classificacao_final = "🟢 Bull Forte"
        elif score_consolidado >= 6.1:
            classificacao_final = "🔵 Bull Moderado"
        elif score_consolidado >= 4.1:
            classificacao_final = "🟡 Tendência Neutra"
        elif score_consolidado >= 2.1:
            classificacao_final = "🟠 Bear Leve"
        else:
            classificacao_final = "🔴 Bear Forte"
            
        # Gerar observação
        observacoes = []
        for ind in indicadores:
            nome = ind["indicador"].split()[0]
            score_ind = ind["score"]
            if score_ind >= 8:
                observacoes.append(f"{nome}: forte ({score_ind})")
            elif score_ind >= 6:
                observacoes.append(f"{nome}: moderado ({score_ind})")
            elif score_ind <= 3:
                observacoes.append(f"{nome}: fraco ({score_ind})")
        
        observacao_final = f"Score consolidado {score_consolidado:.2f}. Destaques: {', '.join(observacoes[:3])}"
        
        return {
            "categoria": "Análise de Ciclos do BTC",
            "score_consolidado": round(score_consolidado, 2),
            "classificacao": classificacao_final,
            "Observação": observacao_final,
            "indicadores": indicadores
        }
        
    except Exception as e:
        logging.error(f"Erro na análise de ciclos: {str(e)}")
        return {
            "categoria": "Análise de Ciclos do BTC",
            "score_consolidado": 0.0,
            "classificacao": "🔴 Erro",
            "Observação": f"Erro na análise: {str(e)}",
            "indicadores": []
        }