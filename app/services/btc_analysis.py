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
            "score_ponderado (score × peso)": score * 0.25,
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
            "score_ponderado (score × peso)": 0.0,
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

def get_realized_price_vs_price_atual(tv: TvDatafeed):
    try:
        df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=Interval.in_daily, n_bars=1)
        preco_atual = df.iloc[-1]["close"]
        realized_price = 24000.0

        variacao_pct = ((preco_atual - realized_price) / realized_price) * 100

        if variacao_pct > 15:
            pontos = 2
        elif variacao_pct >= 0:
            pontos = 1
        else:
            pontos = 0

        return {
            "indicador": "BTC vs Realized Price",
            "fonte": "Realized Price (fixado)",
            "valor": f"{variacao_pct:.2f}%",
            "preco_atual": round(preco_atual, 2),
            "realized_price": round(realized_price, 2),
            "pontuacao_bruta": pontos,
            "peso": 0.25,
            "pontuacao_ponderada": round(pontos * 0.25, 2)
        }

    except Exception as e:
        return {
            "indicador": "BTC vs Realized Price",
            "fonte": "Realized Price (fixado)",
            "valor": "erro",
            "preco_atual": None,
            "realized_price": None,
            "pontuacao_bruta": 0,
            "peso": 0.25,
            "pontuacao_ponderada": 0.0,
            "erro": str(e)
        }

def get_puell_multiple():
    try:
        from notion_client import Client
        settings = get_settings()
        NOTION_TOKEN = settings.NOTION_TOKEN
        
        # Obter o ID do banco de dados e verificar se é válido
        DATABASE_ID = settings.NOTION_DATABASE_ID_MACRO.strip().replace('"', '')
        
        # Verificar se o DATABASE_ID não está vazio
        if not DATABASE_ID:
            logging.error("DATABASE_ID está vazio. Verifique a variável NOTION_DATABASE_ID_MACRO no arquivo .env")
            raise ValueError("DATABASE_ID não pode ser vazio.")
            
        logging.info(f"Puell Multiple - DATABASE_ID: {DATABASE_ID}")
        notion = Client(auth=NOTION_TOKEN)

        response = notion.databases.query(database_id=DATABASE_ID)
        for row in response["results"]:
            props = row["properties"]
            nome = props["indicador"]["title"][0]["plain_text"].strip().lower()
            if nome == "puell_multiple":
                valor = float(props["valor"]["number"])

                if 0.3 <= valor <= 1.5:
                    pontos = 2
                elif 1.5 < valor <= 2.5:
                    pontos = 1
                else:
                    pontos = 0

                return {
                    "indicador": "Puell Multiple",
                    "fonte": "Notion API",
                    "valor": round(valor, 2),
                    "pontuacao_bruta": pontos,
                    "peso": 0.20,
                    "pontuacao_ponderada": round(pontos * 0.20, 2)
                }

        raise ValueError("Indicador 'puell_multiple' não encontrado.")
    except Exception as e:
        return {
            "indicador": "Puell Multiple",
            "fonte": "Notion API",
            "valor": "erro",
            "pontuacao_bruta": 0,
            "peso": 0.20,
            "pontuacao_ponderada": 0.0,
            "erro": str(e)
        }

def get_juros_tendencia(tv: TvDatafeed):
    try:
        exchanges = ["TVC", "ECONOMICS", "INDEX", "FX_IDC"]
        df = None
        fonte_usada = None

        for ex in exchanges:
            df = tv.get_hist(symbol="US10Y", exchange=ex, interval=Interval.in_daily, n_bars=90)
            if df is not None and not df.empty:
                fonte_usada = ex
                break

        if df is None or df.empty:
            raise ValueError("US10Y não encontrado em nenhuma exchange válida.")

        valor_atual = df["close"].iloc[-1]
        valor_passado = df["close"].iloc[0]
        variacao_pct = ((valor_atual - valor_passado) / valor_passado) * 100

        if variacao_pct <= -5:
            pontos = 2
        elif -5 < variacao_pct < 5:
            pontos = 1
        else:
            pontos = 0

        return {
            "indicador": "Juros (US10Y - 90d)",
            "fonte": f"TradingView ({fonte_usada})",
            "valor_atual": round(valor_atual, 2),
            "valor_90d_atras": round(valor_passado, 2),
            "variacao_pct": round(variacao_pct, 2),
            "pontuacao_bruta": pontos,
            "peso": 0.10,
            "pontuacao_ponderada": round(pontos * 0.10, 2)
        }

    except Exception as e:
        return {
            "indicador": "Juros (US10Y - 90d)",
            "fonte": "TradingView",
            "valor_atual": None,
            "valor_90d_atras": None,
            "variacao_pct": None,
            "pontuacao_bruta": 0,
            "peso": 0.10,
            "pontuacao_ponderada": 0.0,
            "erro": str(e)
        }

def get_expansao_global_from_notion():
    try:
        from notion_client import Client
        settings = get_settings()
        NOTION_TOKEN = settings.NOTION_TOKEN
        
        # Obter o ID do banco de dados e verificar se é válido
        DATABASE_ID = settings.NOTION_DATABASE_ID_MACRO.strip().replace('"', '')
        
        # Verificar se o DATABASE_ID não está vazio
        if not DATABASE_ID:
            logging.error("DATABASE_ID está vazio. Verifique a variável NOTION_DATABASE_ID_MACRO no arquivo .env")
            raise ValueError("DATABASE_ID não pode ser vazio.")
            
        logging.info(f"Expansão Global - DATABASE_ID: {DATABASE_ID}")
        notion = Client(auth=NOTION_TOKEN)

        response = notion.databases.query(database_id=DATABASE_ID)
        for row in response["results"]:
            props = row["properties"]
            nome = props["indicador"]["title"][0]["plain_text"].strip().lower()
            if nome == "expansao_global":
                valor = float(props["valor"]["number"])

                if valor > 2.0:
                    pontos = 2
                elif 0.0 <= valor <= 2.0:
                    pontos = 1
                else:
                    pontos = 0

                return {
                    "indicador": "Expansão Global",
                    "fonte": "Notion API",
                    "valor": round(valor, 2),
                    "pontuacao_bruta": pontos,
                    "peso": 0.25,
                    "pontuacao_ponderada": round(pontos * 0.25, 2)
                }

        raise ValueError("Indicador 'expansao_global' não encontrado.")
    except Exception as e:
        return {
            "indicador": "Expansão Global",
            "fonte": "Notion API",
            "valor": "erro",
            "pontuacao_bruta": 0,
            "peso": 0.25,
            "pontuacao_ponderada": 0.0,
            "erro": str(e)
        }

def get_btc_dominance_tendencia(tv: TvDatafeed):
    try:
        df = tv.get_hist(symbol="BTC.D", exchange="CRYPTOCAP", interval=Interval.in_daily, n_bars=30)

        if df is None or df.empty:
            raise ValueError("BTC.D não retornou dados.")

        valor_atual = df["close"].iloc[-1]
        valor_30d_atras = df["close"].iloc[0]
        variacao_pct = ((valor_atual - valor_30d_atras) / valor_30d_atras) * 100

        if variacao_pct >= 2:
            pontos = 2
            tendencia = "alta"
        elif variacao_pct <= -2:
            pontos = 0
            tendencia = "queda"
        else:
            pontos = 1
            tendencia = "estável"

        return {
            "indicador": "BTC Dominance Tendência",
            "fonte": "TradingView (BTC.D)",
            "valor_atual": round(valor_atual, 2),
            "valor_30d_atras": round(valor_30d_atras, 2),
            "variacao_pct": round(variacao_pct, 2),
            "tendencia": tendencia,
            "pontuacao_bruta": pontos,
            "peso": 0.20,
            "pontuacao_ponderada": round(pontos * 0.20, 2)
        }

    except Exception as e:
        return {
            "indicador": "BTC Dominance Tendência",
            "fonte": "TradingView (BTC.D)",
            "valor_atual": None,
            "valor_30d_atras": None,
            "variacao_pct": None,
            "tendencia": "erro",
            "pontuacao_bruta": 0,
            "peso": 0.20,
            "pontuacao_ponderada": 0.0,
            "erro": str(e)
        }

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
            "score_ponderado (score × peso)": score * 0.15,
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
            "score_ponderado (score × peso)": 5.0 * 0.15,
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

# Alternativamente, se precisar passar o TV como parâmetro:
def get_m2_global_momentum_wrapper(tv: TvDatafeed):
    """Wrapper para usar M2 Global com TvDatafeed existente"""
    try:
        from app.utils.m2_utils import get_m2_global_momentum
        return get_m2_global_momentum(tv)
    except Exception as e:
        logging.error(f"Erro M2 Global: {str(e)}")
        # Fallback para Notion se APIs falharem
        raise Exception(f"M2 Global indisponível: {str(e)}")

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

# FUNÇÃO V2.0 ATUALIZADA
def analyze_btc_cycles_v2(tv):
    """Análise de ciclos BTC v2.0 - formato JSON padronizado"""
    try:
        indicadores = []
        
        # 1. BTC vs EMA 200D (30%) - Convertido para escala 0-10
        btc_ema_data = get_btc_vs_200d_ema(tv)
        variacao = btc_ema_data["detalhes"]["variacao_percentual"]
        
        if variacao > 20:
            score_ema = 9.0
            classificacao_ema = "Bull Confirmado"
        elif variacao > 10:
            score_ema = 8.0
            classificacao_ema = "Bull Confirmado"  
        elif variacao > 0:
            score_ema = 7.0
            classificacao_ema = "Bull Inicial"
        elif variacao > -10:
            score_ema = 5.0
            classificacao_ema = "Transição"
        elif variacao > -30:
            score_ema = 3.0
            classificacao_ema = "Bear Moderado"
        else:
            score_ema = 1.0
            classificacao_ema = "Bear Severo"
            
        indicadores.append({
            "indicador": "BTC vs EMA 200D",
            "fonte": "TradingView",
            "valor_coletado": f"BTC {variacao:.1f}% vs EMA 200D",
            "score": score_ema,
            "score_ponderado (score × peso)": score_ema * 0.30,
            "classificacao": classificacao_ema,
            "observação": "Compara preço atual do BTC com média móvel de 200 dias para identificar tendência macro"
        })
        
        # 2. BTC vs Realized Price (30%) - Usando dados do Notion
        try:
            from notion_client import Client
            settings = get_settings()
            notion = Client(auth=settings.NOTION_TOKEN)
            DATABASE_ID = settings.NOTION_DATABASE_ID_MACRO.strip().replace('"', '')
            
            realized_price = 50000  # Default
            response = notion.databases.query(database_id=DATABASE_ID)
            for row in response["results"]:
                props = row["properties"]
                nome = props["indicador"]["title"][0]["plain_text"].strip().lower()
                if nome == "realized_price":
                    realized_price = float(props["valor"]["number"])
                    break
        except:
            realized_price = 50000
            
        # Pegar preço atual do BTC
        btc_current = btc_ema_data["preco_atual"]
        percentual_realized = ((btc_current - realized_price) / realized_price) * 100
        
        if percentual_realized > 50:
            score_realized = 9.0
            classificacao_realized = "Ciclo Aquecido"
        elif percentual_realized > 20:
            score_realized = 7.0
            classificacao_realized = "Ciclo Normal"
        elif percentual_realized > -10:
            score_realized = 5.0
            classificacao_realized = "Acumulação"
        elif percentual_realized > -30:
            score_realized = 3.0
            classificacao_realized = "Capitulação Leve"
        else:
            score_realized = 1.0
            classificacao_realized = "Capitulação Severa"
            
        indicadores.append({
            "indicador": "BTC vs Realized Price",
            "fonte": "Notion API / Glassnode",
            "valor_coletado": f"BTC {percentual_realized:.1f}% vs Realized Price",
            "score": score_realized,
            "score_ponderado (score × peso)": score_realized * 0.30,
            "classificacao": classificacao_realized,
            "observação": "Compara preço de mercado com preço médio pago pelos holders para avaliar fase do ciclo"
        })
        
        # 3. Puell Multiple (20%)
        puell_data = get_puell_multiple()
        puell_value = puell_data.get("valor", 1.0)
        
        if isinstance(puell_value, str):
            puell_value = 1.0
            
        if 0.5 <= puell_value <= 1.2:
            score_puell = 9.0
            classificacao_puell = "Zona Ideal"
        elif 1.2 < puell_value <= 1.8:
            score_puell = 7.0
            classificacao_puell = "Leve Aquecimento"
        elif (0.3 <= puell_value < 0.5) or (1.8 < puell_value <= 2.5):
            score_puell = 5.0
            classificacao_puell = "Neutro"
        elif 2.5 < puell_value <= 4.0:
            score_puell = 3.0
            classificacao_puell = "Tensão Alta"
        else:
            score_puell = 1.0
            classificacao_puell = "Extremo"
            
        indicadores.append({
            "indicador": "Puell Multiple",
            "fonte": "Notion API / Glassnode",
            "valor_coletado": f"{puell_value:.2f}",
            "score": score_puell,
            "score_ponderado (score × peso)": score_puell * 0.20,
            "classificacao": classificacao_puell,
            "observação": "Ratio da receita diária dos mineradores vs média de 1 ano - indica pressão de venda"
        })
        
        # 4. M2 Global Momentum (15%) - NOVA IMPLEMENTAÇÃO
        m2_momentum_data = get_m2_global_momentum()
        indicadores.append(m2_momentum_data)
        
        # 5. Funding Rates 7D (5%) - Usando API Binance
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
        except:
            avg_7d = 0.05
            
        if 0 <= avg_7d <= 0.1:
            score_funding = 9.0
            classificacao_funding = "Sentimento Equilibrado"
        elif 0.1 < avg_7d <= 0.2:
            score_funding = 7.0
            classificacao_funding = "Otimismo Moderado"
        elif 0.2 < avg_7d <= 0.3:
            score_funding = 5.0
            classificacao_funding = "Aquecimento"
        elif 0.3 < avg_7d <= 0.5:
            score_funding = 3.0
            classificacao_funding = "Euforia Inicial"
        else:
            score_funding = 1.0
            classificacao_funding = "Euforia Extrema"
            
        indicadores.append({
            "indicador": "Funding Rates 7D Média",
            "fonte": "Binance API",
            "valor_coletado": f"{avg_7d:.3f}%",
            "score": score_funding,
            "score_ponderado (score × peso)": score_funding * 0.05,
            "classificacao": classificacao_funding,
            "observação": "Média de 7 dias das taxas de funding dos contratos perpétuos - indica sentimento do mercado"
        })
        
        # Calcular score consolidado
        score_consolidado = sum([ind["score_ponderado (score × peso)"] for ind in indicadores])
        
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
        return {
            "categoria": "Análise de Ciclos do BTC",
            "score_consolidado": 0.0,
            "classificacao": "🔴 Erro",
            "Observação": f"Erro na análise: {str(e)}",
            "indicadores": []
        }