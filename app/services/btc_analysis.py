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
            "score_ponderado (score × peso)": 0.0,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro: {str(e)}",
            "detalhes": {
                "preco_atual": None,
                "ema_200": None,
                "variacao_percentual": None
            }
        }


# função _classify_bull_market_strength removida - sem uso para a API analise de ciclos


def get_btc_vs_realized_price(tv: TvDatafeed):
    """
    Analisa a fase do ciclo baseado na posição do BTC vs Realized Price
    Retorna score de 0-10 com classificação em 5 níveis
    """
    try:
        # Buscar preço atual do BTC
        df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=Interval.in_daily, n_bars=1)
        preco_atual = df.iloc[-1]["close"]
        
        # Buscar Realized Price do Notion
        realized_price = _get_realized_price_from_notion()
        
        variacao_pct = ((preco_atual - realized_price) / realized_price) * 100

        # Classificar fase do ciclo
        score, classificacao = _classify_cycle_phase(variacao_pct)

        return {
            "indicador": "BTC vs Realized Price",
            "fonte": "Notion API / Glassnode",
            "valor_coletado": f"BTC {variacao_pct:.1f}% vs Realized Price",
            "score": score,
            f"score_ponderado ({score} × 0.30)": score * 0.30,
            "classificacao": classificacao,
            "observação": "Compara preço de mercado com preço médio pago pelos holders para avaliar fase do ciclo",
            "detalhes": {
                "preco_atual": round(preco_atual, 2),
                "realized_price": round(realized_price, 2),
                "variacao_percentual": round(variacao_pct, 2)
            }
        }

    except Exception as e:
        return {
            "indicador": "BTC vs Realized Price",
            "fonte": "Notion API / Glassnode",
            "valor_coletado": "erro",
            "score": 0.0,
            "score_ponderado (score × peso)": 0.0,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro: {str(e)}",
            "detalhes": {
                "preco_atual": None,
                "realized_price": None,
                "variacao_percentual": None
            }
        }


# função _get_realized_price_from_notion removida - sem uso para a API analise de ciclos


# função _classify_cycle_phase removida - sem uso para a API analise de ciclos


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
            "score_ponderado (score × peso)": 0.0,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro: {str(e)}",
            "detalhes": {
                "puell_value": None
            }
        }


# função _classify_miner_pressure removida - sem uso para a API analise de ciclos


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
            "score_ponderado (score × peso)": 0.0,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro: {str(e)}",
            "detalhes": {
                "funding_rate_7d": None
            }
        }


# função _classify_market_sentiment removida - sem uso para a API analise de ciclos


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
            "score_ponderado (score × peso)": 5.0 * 0.15,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro: {str(e)}"
        }


# função _get_m2_from_apis removida - sem uso para a API analise de ciclos


# função _get_m2_from_notion removida - sem uso para a API analise de ciclos


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
        
        # Calcular score consolidado
        score_consolidado = sum([list(ind.values())[4] for ind in indicadores if len(ind.values()) > 4])
        
        # Classificação final
        if score_consolidado >= 8.1:
            classificacao_final = "Bull Forte"
        elif score_consolidado >= 6.1:
            classificacao_final = "Bull Moderado"
        elif score_consolidado >= 4.1:
            classificacao_final = "Tendência Neutra"
        elif score_consolidado >= 2.1:
            classificacao_final = "Bear Leve"
        else:
            classificacao_final = "Bear Forte"
            
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