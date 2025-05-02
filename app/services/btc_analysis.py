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
