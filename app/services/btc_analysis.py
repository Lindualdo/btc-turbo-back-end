from tvDatafeed import TvDatafeed, Interval

def get_btc_vs_200d_ema(tv: TvDatafeed):
    try:
        df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=Interval.in_daily, n_bars=250)
        df["EMA_200"] = df["close"].ewm(span=200, adjust=False).mean()
        latest = df.iloc[-1]
        close = latest["close"]
        ema200 = latest["EMA_200"]
        variacao_pct = ((close - ema200) / ema200) * 100

        if variacao_pct > 10:
            pontos = 2
        elif variacao_pct >= 0:
            pontos = 1
        else:
            pontos = 0

        if 9.5 <= variacao_pct <= 10.5:
            confiabilidade = "95%"
        else:
            confiabilidade = "100%"

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