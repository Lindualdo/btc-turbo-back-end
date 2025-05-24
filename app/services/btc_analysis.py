import os
import math
from tvDatafeed import TvDatafeed, Interval
import requests
from app.config import get_settings
import logging
from app.utils.m2_utils import get_m2_global_momentum
from app.utils.realized_price_utils import analyze_btc_vs_realized_price


def safe_division(numerator, denominator, fallback=0.0):
    """Divisão segura que evita NaN, Infinity e None"""
    try:
        
    except Exception as e:
        return {
            "indicador": "Funding Rates 7D Média",
            "fonte": "Binance API",
            "valor_coletado": "erro",
            "score": 0.0,
            "score_ponderado (score × peso)": 0.0,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro ao coletar Funding Rates: {str(e)}. Verifique conexão com Binance API.",
            "detalhes": {
                "dados_coletados": {
                    "funding_rate_7d": 0.0,
                    "total_coletas": 0,
                    "exchange": "Binance",
                    "simbolo": "BTCUSDT"
                },
                "calculo": {
                    "formula": "Soma(Funding_Rates_7D) / Total_Períodos",
                    "taxa_media": 0.0,
                    "faixa_classificacao": "N/A"
                },
                "racional": "Dados indisponíveis devido a erro na coleta"
            }
        }


def _classify_market_sentiment(avg_7d):
    """Classifica o sentimento do mercado - Score máximo 10.0"""
    avg_7d = safe_float(avg_7d)
    
    if 0 <= avg_7d <= 0.1:
        return 10.0, "Sentimento Equilibrado"
    elif 0.1 < avg_7d <= 0.2:
        return 8.0, "Otimismo Moderado"
    elif 0.2 < avg_7d <= 0.3:
        return 6.0, "Aquecimento"
    elif 0.3 < avg_7d <= 0.5:
        return 4.0, "Euforia Inicial"
    else:
        return 2.0, "Euforia Extrema"


def _get_funding_range(avg_7d):
    """Retorna a faixa de classificação para Funding Rates"""
    avg_7d = safe_float(avg_7d)
    
    if 0 <= avg_7d <= 0.1:
        return "0% - 0.1%"
    elif 0.1 < avg_7d <= 0.2:
        return "0.1% - 0.2%"
    elif 0.2 < avg_7d <= 0.3:
        return "0.2% - 0.3%"
    elif 0.3 < avg_7d <= 0.5:
        return "0.3% - 0.5%"
    else:
        return "> 0.5%"


def get_m2_global_momentum():
    """M2 Global Momentum Score - MANTIDO (será refatorado no próximo passo)"""
    try:
        logging.info("🚀 Iniciando coleta M2 Global Momentum...")
        
        # Tentar APIs primeiro
        try:
            momentum_value = _get_m2_from_apis()
            fonte = "TradingView APIs"
        except Exception as api_error:
            logging.warning(f"⚠️ APIs TradingView falharam: {str(api_error)}")
            momentum_value = _get_m2_from_notion()
            fonte = "Notion API"
        
        momentum_value = safe_float(momentum_value)
        
        # Classificar momentum - Score máximo 10.0
        if momentum_value > 3:
            score = 10.0
            classificacao = "Aceleração Forte"
        elif momentum_value > 1:
            score = 8.0
            classificacao = "Aceleração Moderada"
        elif momentum_value > -1:
            score = 6.0
            classificacao = "Estável"
        elif momentum_value > -3:
            score = 4.0
            classificacao = "Desaceleração"
        else:
            score = 2.0
            classificacao = "Contração"
            
        return {
            "indicador": "M2 Global Momentum",
            "fonte": fonte,
            "valor_coletado": f"{momentum_value:.1f}% momentum",
            "score": safe_float(score),
            f"score_ponderado ({score} × 0.15)": safe_float(score * 0.15),
            "classificacao": classificacao,
            "observação": "Velocidade de mudança na expansão monetária global - indica aceleração ou desaceleração de liquidez",
            "detalhes": {
                "dados_coletados": {
                    "momentum_value": safe_float(momentum_value),
                    "fonte": fonte.split(" ")[0]
                },
                "calculo": {
                    "formula": "Taxa_Crescimento_M2_Trimestral_Anualizada",
                    "momentum_anualizado": safe_float(momentum_value),
                    "faixa_classificacao": _get_m2_range(momentum_value)
                },
                "racional": f"Momentum de {momentum_value:.1f}% indica {classificacao.lower()} na expansão monetária global"
            }
        }
        
    except Exception as e:
        logging.error(f"❌ Erro crítico M2 Global: {str(e)}")
        return {
            "indicador": "M2 Global Momentum", 
            "fonte": "Erro",
            "valor_coletado": "erro",
            "score": 0.0,
            "score_ponderado (score × peso)": 0.0,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro ao coletar M2 Global: {str(e)}. Verifique conexão com APIs ou Notion.",
            "detalhes": {
                "dados_coletados": {
                    "momentum_value": 0.0,
                    "fonte": "N/A"
                },
                "calculo": {
                    "formula": "Taxa_Crescimento_M2_Trimestral_Anualizada",
                    "momentum_anualizado": 0.0,
                    "faixa_classificacao": "N/A"
                },
                "racional": "Dados indisponíveis devido a erro na coleta"
            }
        }


def _get_m2_range(momentum_value):
    """Retorna a faixa de classificação para M2 Global Momentum"""
    momentum_value = safe_float(momentum_value)
    
    if momentum_value > 3:
        return "> +3%"
    elif momentum_value > 1:
        return "+1% a +3%"
    elif momentum_value > -1:
        return "-1% a +1%"
    elif momentum_value > -3:
        return "-3% a -1%"
    else:
        return "< -3%"


def _get_m2_from_apis():
    """Busca M2 das APIs - MANTIDO"""
    try:
        from app.utils.m2_utils import get_m2_global_momentum as m2_utils_function
        momentum_value = m2_utils_function()
        return safe_float(momentum_value, 2.0)
    except Exception as e:
        logging.error(f"❌ Erro ao buscar M2 via utils: {str(e)}")
        raise Exception(f"APIs M2 indisponíveis: {str(e)}")


def _get_m2_from_notion():
    """Busca M2 do Notion - MANTIDO"""
    try:
        from notion_client import Client
        settings = get_settings()
        notion = Client(auth=settings.NOTION_TOKEN)
        DATABASE_ID = settings.NOTION_DATABASE_ID_MACRO.strip().replace('"', '')
        
        response = notion.databases.query(database_id=DATABASE_ID)
        
        for row in response["results"]:
            props = row["properties"]
            nome = props["indicador"]["title"][0]["plain_text"].strip().lower()
            
            if nome in ["m2_global", "m2_momentum", "expansao_global"]:
                valor = safe_float(props["valor"]["number"], 2.0)
                return valor
                
        return 2.0
        
    except Exception as e:
        logging.error(f"❌ Erro Notion M2: {str(e)}")
        return 2.0


def _generate_resumo_executivo(score_consolidado):
    """Gera resumo executivo baseado no score consolidado"""
    score_consolidado = safe_float(score_consolidado)
    
    if score_consolidado >= 8.1:
        return {
            "estrategia_recomendada": "Operações Agressivas",
            "exposicao_sugerida": "Alavancagem alta (3-5x), exposição máxima ao BTC",
            "gestao_risco": "Stop loss moderado, trailing stops para capturar tendência",
            "outlook": "Ambiente ideal para hold alavancado - todos os indicadores favoráveis"
        }
    elif score_consolidado >= 6.1:
        return {
            "estrategia_recomendada": "Operações com Cautela",
            "exposicao_sugerida": "Alavancagem moderada (2-3x máximo)",
            "gestao_risco": "Monitoramento constante, stop loss apertado",
            "outlook": "Ambiente favorável mas com necessidade de cautela"
        }
    elif score_consolidado >= 4.1:
        return {
            "estrategia_recomendada": "Aguardar Definição",
            "exposicao_sugerida": "Evitar alavancagem, posições pequenas se houver",
            "gestao_risco": "Preservação de capital como prioridade máxima",
            "outlook": "Mercado indefinido - aguardar sinais mais claros"
        }
    elif score_consolidado >= 2.1:
        return {
            "estrategia_recomendada": "Posições Defensivas",
            "exposicao_sugerida": "Reduzir exposição, considerar hedge parcial",
            "gestao_risco": "Stop loss muito apertado, gestão rigorosa",
            "outlook": "Condições desfavoráveis - foco em proteção"
        }
    else:
        return {
            "estrategia_recomendada": "Evitar Operações de Alta",
            "exposicao_sugerida": "Cash ou hedge completo, aguardar reversão",
            "gestao_risco": "Não operar alta - risco muito elevado",
            "outlook": "Ciclo de baixa confirmado - aguardar fundo"
        }


# FUNÇÃO PRINCIPAL - REFATORADA E LIMPA
def analyze_btc_cycles(tv):
    """
    Análise de ciclos BTC - VERSÃO REFATORADA
    - Realized Price via UTXOs blockchain REAIS (novo utilitário)
    - Score máximo 10.0 em todos indicadores
    - Validações de segurança JSON
    - Campo detalhes completo e padronizado
    - Resumo executivo incluído
    - Código mais limpo e organizado
    """
    try:
        indicadores = []
        
        # 1. BTC vs EMA 200D (30%) - TradingView
        logging.info("📊 Coletando BTC vs EMA 200D...")
        btc_ema_data = get_btc_vs_200d_ema(tv)
        indicadores.append(btc_ema_data)
        
        # 2. BTC vs Realized Price (30%) - UTXOs BLOCKCHAIN REAIS (NOVO!)
        logging.info("🔗 Coletando BTC vs Realized Price via UTXOs reais...")
        realized_data = get_btc_vs_realized_price(tv)
        indicadores.append(realized_data)
        
        # 3. Puell Multiple (20%) - Notion (próximo a ser refatorado)
        logging.info("⛏️ Coletando Puell Multiple...")
        puell_data = get_puell_multiple()
        indicadores.append(puell_data)
        
        # 4. M2 Global Momentum (15%) - TradingView + Notion fallback
        logging.info("💰 Coletando M2 Global Momentum...")
        m2_data = get_m2_global_momentum()
        indicadores.append(m2_data)
        
        # 5. Funding Rates 7D (5%) - Binance API
        logging.info("📈 Coletando Funding Rates...")
        funding_data = get_funding_rates_analysis()
        indicadores.append(funding_data)
        
        # Calcular score consolidado SEGURO
        scores_ponderados = []
        for ind in indicadores:
            for key, value in ind.items():
                if "score_ponderado" in key and isinstance(value, (int, float)):
                    scores_ponderados.append(safe_float(value))
                    break
        
        score_consolidado = safe_float(sum(scores_ponderados))
        
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
            score_ind = safe_float(ind["score"])
            if score_ind >= 8:
                observacoes.append(f"{nome}: forte ({score_ind})")
            elif score_ind >= 6:
                observacoes.append(f"{nome}: moderado ({score_ind})")
            elif score_ind <= 3:
                observacoes.append(f"{nome}: fraco ({score_ind})")
        
        observacao_final = f"Score consolidado {score_consolidado:.2f}. Destaques: {', '.join(observacoes[:3])}"
        
        # Gerar resumo executivo
        resumo_executivo = _generate_resumo_executivo(score_consolidado)
        
        logging.info(f"✅ Análise de ciclos concluída - Score: {score_consolidado:.2f} - {classificacao_final}")
        
        return {
            "categoria": "Análise de Ciclos do BTC",
            "score_consolidado": safe_float(score_consolidado),
            "classificacao": classificacao_final,
            "observacao": observacao_final,
            "resumo_executivo": resumo_executivo,
            "indicadores": indicadores
        }
        
    except Exception as e:
        logging.error(f"❌ Erro na análise de ciclos: {str(e)}")
        return {
            "categoria": "Análise de Ciclos do BTC",
            "score_consolidado": 0.0,
            "classificacao": "🔴 Erro",
            "observacao": f"Erro na análise: {str(e)}",
            "resumo_executivo": {
                "estrategia_recomendada": "Sistema Indisponível",
                "exposicao_sugerida": "Aguardar resolução do erro",
                "gestao_risco": "Não operar até sistema estar funcional",
                "outlook": "Erro técnico - consulte administrador do sistema"
            },
            "indicadores": []
        }


# PRÓXIMOS PASSOS DE REFATORAÇÃO:
# 
# 🔄 TODO - Criar utilitários separados:
# - app/utils/puell_multiple_utils.py  
# - app/utils/funding_rates_utils.py
# - app/utils/bull_market_utils.py
# - app/utils/m2_momentum_utils.py (melhorar o existente)
#
# 🎯 OBJETIVO: Deixar este arquivo apenas como proxy/orquestrador
# Cada indicador em seu próprio utilitário para melhor organizaçãoif denominator == 0 or denominator is None or numerator is None:
            return fallback
        
        result = numerator / denominator
        
        if math.isnan(result) or math.isinf(result):
            return fallback
            
        return result
    except (TypeError, ZeroDivisionError):
        return fallback


def safe_float(value, fallback=0.0):
    """Converte valor para float seguro para JSON"""
    try:
        if value is None:
            return fallback
        
        result = float(value)
        
        if math.isnan(result) or math.isinf(result):
            return fallback
            
        return result
    except (TypeError, ValueError):
        return fallback


def get_btc_vs_200d_ema(tv: TvDatafeed):
    """
    Analisa a força do bull market baseado na posição do BTC vs EMA 200D
    Retorna score de 0-10 com classificação em 5 níveis
    """
    try:
        df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=Interval.in_daily, n_bars=250)
        df["EMA_200"] = df["close"].ewm(span=200, adjust=False).mean()
        latest = df.iloc[-1]
        close = safe_float(latest["close"])
        ema200 = safe_float(df["EMA_200"].iloc[-1])
        
        if close <= 0 or ema200 <= 0:
            raise ValueError("Preços inválidos coletados")
        
        variacao_pct = safe_division((close - ema200), ema200, 0.0) * 100
        score, classificacao = _classify_bull_market_strength(variacao_pct)

        return {
            "indicador": "BTC vs EMA 200D",
            "fonte": "TradingView",
            "valor_coletado": f"BTC {variacao_pct:.1f}% vs EMA 200D",
            "score": safe_float(score),
            f"score_ponderado ({score} × 0.30)": safe_float(score * 0.30),
            "classificacao": classificacao,
            "observação": "Força do bull market baseada na distância do preço atual vs EMA 200 dias",
            "detalhes": {
                "dados_coletados": {
                    "preco_atual": safe_float(close),
                    "ema_200": safe_float(ema200),
                    "fonte": "TradingView/Binance"
                },
                "calculo": {
                    "formula": f"(({close:.0f} - {ema200:.0f}) / {ema200:.0f}) × 100",
                    "variacao_percentual": safe_float(variacao_pct),
                    "faixa_classificacao": _get_bull_market_range(variacao_pct)
                },
                "racional": f"Preço {variacao_pct:.1f}% vs EMA 200D indica {classificacao.lower()} com base na distância histórica"
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
            "observação": f"Erro ao coletar dados TradingView: {str(e)}. Verifique conexão ou credenciais.",
            "detalhes": {
                "dados_coletados": {
                    "preco_atual": 0.0,
                    "ema_200": 0.0,
                    "fonte": "TradingView/Binance"
                },
                "calculo": {
                    "formula": "((Preço_Atual - EMA_200) / EMA_200) × 100",
                    "variacao_percentual": 0.0,
                    "faixa_classificacao": "N/A"
                },
                "racional": "Dados indisponíveis devido a erro na coleta"
            }
        }


def _classify_bull_market_strength(variacao_pct):
    """Classifica a força do bull market - Score máximo 10.0"""
    variacao_pct = safe_float(variacao_pct)
    
    if variacao_pct > 30:
        return 10.0, "Bull Parabólico"
    elif variacao_pct > 15:
        return 8.0, "Bull Forte"  
    elif variacao_pct > 5:
        return 6.0, "Bull Moderado"
    elif variacao_pct > 0:
        return 4.0, "Bull Inicial"
    else:
        return 2.0, "Bull Não Confirmado"


def _get_bull_market_range(variacao_pct):
    """Retorna a faixa de classificação para o bull market"""
    variacao_pct = safe_float(variacao_pct)
    
    if variacao_pct > 30:
        return "> +30%"
    elif variacao_pct > 15:
        return "+15% a +30%"
    elif variacao_pct > 5:
        return "+5% a +15%"
    elif variacao_pct > 0:
        return "0% a +5%"
    else:
        return "< 0%"


def get_btc_vs_realized_price(tv: TvDatafeed):
    """
    NOVA VERSÃO: Usa utilitário com dados REAIS de UTXOs blockchain
    """
    try:
        # Buscar preço atual do BTC
        df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=Interval.in_daily, n_bars=1)
        preco_atual = safe_float(df.iloc[-1]["close"])
        
        if preco_atual <= 0:
            raise ValueError("Preço atual inválido")
        
        # NOVO: Usar utilitário com UTXOs reais
        return analyze_btc_vs_realized_price(preco_atual)
        
    except Exception as e:
        logging.error(f"❌ Erro na análise BTC vs Realized Price: {str(e)}")
        return {
            "indicador": "BTC vs Realized Price",
            "fonte": "UTXOs blockchain reais",
            "valor_coletado": "erro",
            "score": 0.0,
            "score_ponderado (score × peso)": 0.0,
            "classificacao": "Dados indisponíveis",
            "observação": f"Erro ao buscar preço atual BTC: {str(e)}. Verifique conexão TradingView.",
            "detalhes": {
                "dados_coletados": {
                    "preco_atual": 0.0,
                    "realized_price": 0.0,
                    "fonte": "N/A"
                },
                "calculo": {
                    "formula": "((Preço_Atual - Realized_Price) / Realized_Price) × 100",
                    "variacao_percentual": 0.0,
                    "faixa_classificacao": "N/A"
                },
                "racional": "Dados indisponíveis devido a erro na coleta"
            }
        }


def get_puell_multiple():
    """
    Analisa a pressão dos mineradores baseado no Puell Multiple
    MANTIDO: Ainda usa Notion (será refatorado no próximo passo)
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
                valor = safe_float(props["valor"]["number"])
                
                score, classificacao = _classify_miner_pressure(valor)

                return {
                    "indicador": "Puell Multiple",
                    "fonte": "Notion API / Glassnode",
                    "valor_coletado": f"{valor:.2f}",
                    "score": safe_float(score),
                    f"score_ponderado ({score} × 0.20)": safe_float(score * 0.20),
                    "classificacao": classificacao,
                    "observação": "Ratio da receita diária dos mineradores vs média de 1 ano - indica pressão de venda",
                    "detalhes": {
                        "dados_coletados": {
                            "puell_value": safe_float(valor),
                            "fonte": "Notion/Glassnode"
                        },
                        "calculo": {
                            "formula": "Receita_Diária_Mineradores / Média_365_Dias",
                            "resultado": safe_float(valor),
                            "faixa_classificacao": _get_puell_range(valor)
                        },
                        "racional": f"Puell de {valor:.2f} indica {classificacao.lower()} baseado em análise de receita dos mineradores"
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
            "observação": f"Erro ao coletar Puell Multiple: {str(e)}. Verifique conexão Notion ou dados Glassnode.",
            "detalhes": {
                "dados_coletados": {
                    "puell_value": 0.0,
                    "fonte": "Notion/Glassnode"
                },
                "calculo": {
                    "formula": "Receita_Diária_Mineradores / Média_365_Dias",
                    "resultado": 0.0,
                    "faixa_classificacao": "N/A"
                },
                "racional": "Dados indisponíveis devido a erro na coleta"
            }
        }


def _classify_miner_pressure(puell_value):
    """Classifica a pressão dos mineradores - Score máximo 10.0"""
    puell_value = safe_float(puell_value)
    
    if 0.5 <= puell_value <= 1.2:
        return 10.0, "Zona Ideal"
    elif 1.2 < puell_value <= 1.8:
        return 8.0, "Leve Aquecimento"
    elif (0.3 <= puell_value < 0.5) or (1.8 < puell_value <= 2.5):
        return 6.0, "Neutro"
    elif 2.5 < puell_value <= 4.0:
        return 4.0, "Tensão Alta"
    else:
        return 2.0, "Extremo"


def _get_puell_range(puell_value):
    """Retorna a faixa de classificação para Puell Multiple"""
    puell_value = safe_float(puell_value)
    
    if 0.5 <= puell_value <= 1.2:
        return "0.5 - 1.2"
    elif 1.2 < puell_value <= 1.8:
        return "1.2 - 1.8"
    elif (0.3 <= puell_value < 0.5) or (1.8 < puell_value <= 2.5):
        return "0.3-0.5 ou 1.8-2.5"
    elif 2.5 < puell_value <= 4.0:
        return "2.5 - 4.0"
    else:
        return "< 0.3 ou > 4.0"


def get_funding_rates_analysis():
    """Analisa o sentimento do mercado baseado nas Funding Rates"""
    try:
        url = "https://fapi.binance.com/fapi/v1/fundingRate"
        params = {"symbol": "BTCUSDT", "limit": 56}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data:
            rates = [safe_float(item["fundingRate"]) * 100 for item in data if item.get("fundingRate")]
            if rates:
                avg_7d = safe_division(sum(rates), len(rates), 0.0)
            else:
                avg_7d = 0.0
        else:
            avg_7d = 0.0
            
        score, classificacao = _classify_market_sentiment(avg_7d)
        
        return {
            "indicador": "Funding Rates 7D Média",
            "fonte": "Binance API",
            "valor_coletado": f"{avg_7d:.3f}%",
            "score": safe_float(score),
            f"score_ponderado ({score} × 0.05)": safe_float(score * 0.05),
            "classificacao": classificacao,
            "observação": "Média de 7 dias das taxas de funding dos contratos perpétuos - indica sentimento do mercado",
            "detalhes": {
                "dados_coletados": {
                    "funding_rate_7d": safe_float(avg_7d),
                    "total_coletas": len(data) if data else 0,
                    "exchange": "Binance",
                    "simbolo": "BTCUSDT"
                },
                "calculo": {
                    "formula": "Soma(Funding_Rates_7D) / Total_Períodos",
                    "taxa_media": safe_float(avg_7d),
                    "faixa_classificacao": _get_funding_range(avg_7d)
                },
                "racional": f"Funding rate de {avg_7d:.3f}% indica {classificacao.lower()} baseado em análise de sentimento"
            }
        }