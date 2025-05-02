import os
from tvDatafeed import TvDatafeed, Interval
import requests

def get_btc_vs_200d_ema(tv: TvDatafeed):
    try:
        df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=Interval.in_daily, n_bars=250)
        df["EMA_200"] = df["close"].ewm(span=200, adjust=False).mean()
        latest = df.iloc[-1]
        close = latest["close"]
        ema200 = df["EMA_200"].iloc[-1]
        variacao_pct = ((close - ema200) / ema200) * 100

        if variacao_pct > 10:
            pontos = 2
        elif variacao_pct >= 0:
            pontos = 1
        else:
            pontos = 0

        confiabilidade = "95%" if 9.5 <= variacao_pct <= 10.5 else "100%"

        return {
            "indicador": "BTC vs 200D EMA",
            "fonte": "TradingView (tvDatafeed)",
            "valor": f"{variacao_pct:.2f}%",
            "preco_atual": round(close, 2),
            "ema_200": round(ema200, 2),
            "pontuacao_bruta": pontos,
            "peso": 0.25,
            "pontuacao_ponderada": round(pontos * 0.25, 2),
            "confiabilidade": confiabilidade
        }

    except Exception as e:
        return {
            "indicador": "BTC vs 200D EMA",
            "fonte": "TradingView (tvDatafeed)",
            "valor": "erro",
            "preco_atual": None,
            "ema_200": None,
            "pontuacao_bruta": 0,
            "peso": 0.25,
            "pontuacao_ponderada": 0.0,
            "confiabilidade": "erro",
            "erro": str(e)
        }

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
        NOTION_TOKEN = os.getenv("NOTION_TOKEN")
        DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
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

def get_btc_dominance_mock():
    tendencia = "alta"
    if tendencia == "alta":
        pontos = 2
    elif tendencia == "estavel":
        pontos = 1
    else:
        pontos = 0

    return {
        "indicador": "BTC Dominance Tendência",
        "fonte": "Mock (fixado)",
        "valor": tendencia,
        "pontuacao_bruta": pontos,
        "peso": 0.20,
        "pontuacao_ponderada": round(pontos * 0.20, 2)
    }

def get_juros_tendencia(tv: TvDatafeed):
    try:
        df = tv.get_hist(symbol="US10Y", exchange="ECONOMICS", interval=Interval.in_daily, n_bars=90)
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
            "fonte": "TradingView (US10Y)",
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
            "fonte": "TradingView (US10Y)",
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
        NOTION_TOKEN = os.getenv("NOTION_TOKEN")
        DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
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
