# app/services/fundamentals.py

import math
import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from requests.exceptions import HTTPError

COINGECKO_URL     = "https://api.coingecko.com/api/v3/coins/bitcoin"
COINMETRICS_BASE  = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
FRED_M2_CSV       = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=M2SL"

def _fetch_coingecko() -> dict:
    resp = requests.get(
        COINGECKO_URL,
        params={"localization": "false", "tickers": "false", "market_data": "true"}
    )
    resp.raise_for_status()
    md = resp.json().get("market_data", {})
    return {
        "price": md.get("current_price", {}).get("usd", 0),
        "supply": md.get("circulating_supply", 0)
    }

def _fetch_coinmetrics_timeseries(metric: str, days: int = 365) -> (float, float):
    now = datetime.utcnow()
    start = (now - timedelta(days=days)).isoformat()
    end   = now.isoformat()
    params = {
        "assets": "btc",
        "metrics": metric,
        "frequency": "1d",
        "start_time": start,
        "end_time": end
    }
    resp = requests.get(COINMETRICS_BASE, params=params)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    if len(data) >= 2:
        prev = float(data[0].get("value", 0))
        curr = float(data[-1].get("value", 0))
        return prev, curr
    raise ValueError(f"Not enough data for metric '{metric}'")

def get_model_variance() -> dict:
    try:
        from notion_client import Client
        from app.config import get_settings
        settings = get_settings()
        NOTION_TOKEN = settings.NOTION_TOKEN
        
        # Obter o ID do banco de dados e verificar se é válido
        DATABASE_ID = settings.NOTION_DATABASE_ID_MACRO.strip().replace('"', '')
        
        # Verificar se o DATABASE_ID não está vazio
        if not DATABASE_ID:
            logging.error("DATABASE_ID está vazio. Verifique a variável NOTION_DATABASE_ID_MACRO no arquivo .env")
            raise ValueError("DATABASE_ID não pode ser vazio.")
            
        logging.info(f"Model Variance - DATABASE_ID: {DATABASE_ID}")
        notion = Client(auth=NOTION_TOKEN)

        response = notion.databases.query(database_id=DATABASE_ID)
        for row in response["results"]:
            props = row["properties"]
            nome = props["indicador"]["title"][0]["plain_text"].strip().lower()
            if nome == "model_variance":
                valor = float(props["valor"]["number"])

                if valor > 1:
                    score = 3
                elif valor > 0:
                    score = 2
                elif valor > -1:
                    score = 1
                else:
                    score = 0

                peso = 0.35
                return {
                    "indicador": "Model Variance (S2F)",
                    "fonte": "Notion API",
                    "valor": round(valor, 2),
                    "pontuacao_bruta": score,
                    "peso": peso,
                    "pontuacao_ponderada": round((score / 3) * peso, 4)
                }

        raise ValueError("Indicador 'model_variance' não encontrado.")
    except Exception as e:
        peso = 0.35
        return {
            "indicador": "Model Variance (S2F)",
            "fonte": "Notion API",
            "valor": "erro",
            "pontuacao_bruta": 0,
            "peso": peso,
            "pontuacao_ponderada": 0.0,
            "erro": str(e)
        }

def get_mvrv_zscore() -> dict:
    peso = 0.25
    try:
        from notion_client import Client
        from app.config import get_settings
        settings = get_settings()
        NOTION_TOKEN = settings.NOTION_TOKEN
        
        # Obter o ID do banco de dados e verificar se é válido
        DATABASE_ID = settings.NOTION_DATABASE_ID_MACRO.strip().replace('"', '')
        
        # Verificar se o DATABASE_ID não está vazio
        if not DATABASE_ID:
            logging.error("DATABASE_ID está vazio. Verifique a variável NOTION_DATABASE_ID_MACRO no arquivo .env")
            raise ValueError("DATABASE_ID não pode ser vazio.")
            
        logging.info(f"MVRV Z-Score - DATABASE_ID: {DATABASE_ID}")
        notion = Client(auth=NOTION_TOKEN)

        response = notion.databases.query(database_id=DATABASE_ID)
        for row in response["results"]:
            props = row["properties"]
            nome = props["indicador"]["title"][0]["plain_text"].strip().lower()
            if nome == "mvrv":
                valor = float(props["valor"]["number"])

                if valor > 3:
                    score = 3
                elif valor > 1:
                    score = 2
                elif valor > -1:
                    score = 1
                else:
                    score = 0

                return {
                    "indicador": "MVRV Z-Score",
                    "fonte": "Notion API",
                    "valor": round(valor, 2),
                    "pontuacao_bruta": score,
                    "peso": peso,
                    "pontuacao_ponderada": round((score / 3) * peso, 4)
                }

        raise ValueError("Indicador 'mvrv' não encontrado.")
    except Exception as e:
        return {
            "indicador": "MVRV Z-Score",
            "fonte": "Notion API",
            "valor": "erro",
            "pontuacao_bruta": 0,
            "peso": peso,
            "pontuacao_ponderada": 0.0,
            "erro": str(e)
        }

def get_vdd_multiple() -> dict:
    peso = 0.20
    try:
        _, curr = _fetch_coinmetrics_timeseries("VDD.Multiple", days=1)
        value = curr
    except:
        value = 0

    if value > 3:
        score = 3
    elif value > 1:
        score = 2
    elif value > 0.5:
        score = 1
    else:
        score = 0

    return {
        "indicador": "VDD Multiple",
        "valor": round(value, 2),
        "pontuacao_bruta": score,
        "peso": peso,
        "pontuacao_ponderada": round((score / 3) * peso, 4)
    }

def get_m2_global_expansion() -> dict:
    peso = 0.20
    try:
        df = pd.read_csv(FRED_M2_CSV)
        df["DATE"] = pd.to_datetime(df.iloc[:, 0])
        series = df.set_index("DATE")[df.columns[1]]
        latest = series.iloc[-1]
        cutoff = series.index.max() - pd.DateOffset(months=6)
        prev = series[series.index <= cutoff]
        prev_val = prev.iloc[-1] if not prev.empty else series.iloc[0]
        pct6m = (latest / prev_val - 1) * 100
    except:
        pct6m = 0

    if pct6m > 10:
        score = 3
    elif pct6m > 5:
        score = 2
    elif pct6m > 0:
        score = 1
    else:
        score = 0

    return {
        "indicador": "Expansão Global M2 (6m)",
        "valor": round(pct6m, 2),
        "pontuacao_bruta": score,
        "peso": peso,
        "pontuacao_ponderada": round((score / 3) * peso, 4)
    }

def get_all_fundamentals() -> dict:
    indicadores = [
        get_model_variance(),
        get_mvrv_zscore(),
        get_vdd_multiple(),
        get_m2_global_expansion()
    ]
    total_ponderado = sum(i["pontuacao_ponderada"] for i in indicadores)
    score_final = round((total_ponderado / 2) * 10, 2)  # normalização conforme doc
    return {"tabela": indicadores, "consolidado": score_final}