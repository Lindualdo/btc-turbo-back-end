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
        realized_price = 24000.0  # valor fixado

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
        url = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
        params = {
            "assets": "btc",
            "metrics": "puell_multiple",
            "frequency": "1d",
            "limit": 1
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        valor = float(data['data'][0]['puell_multiple'])

        if 0.3 <= valor <= 1.5:
            pontos = 2
        elif 1.5 < valor <= 2.5:
            pontos = 1
        else:
            pontos = 0

        return {
            "indicador": "Puell Multiple",
            "fonte": "Coin Metrics API",
            "valor": round(valor, 2),
            "pontuacao_bruta": pontos,
            "peso": 0.20,
            "pontuacao_ponderada": round(pontos * 0.20, 2)
        }

    except Exception as e:
        return {
            "indicador": "Puell Multiple",
            "fonte": "Coin Metrics API",
            "valor": "erro",
            "pontuacao_bruta": 0,
            "peso": 0.20,
            "pontuacao_ponderada": 0.0,
            "erro": str(e)
        }

def get_btc_dominance_mock():
    tendencia = "alta"  # mock
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

def get_macro_environment_mock():
    contexto = "expansao"  # mock
    if contexto == "expansao":
        pontos = 2
    elif contexto == "estavel":
        pontos = 1
    else:
        pontos = 0

    return {
        "indicador": "Macroambiente (Liquidez/Juros)",
        "fonte": "Mock (fixado)",
        "valor": contexto,
        "pontuacao_bruta": pontos,
        "peso": 0.10,
        "pontuacao_ponderada": round(pontos * 0.10, 2)
    }