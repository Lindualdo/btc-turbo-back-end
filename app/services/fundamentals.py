# app/services/fundamentals.py

import math
import requests
import pandas as pd
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
    a, b = 3.36, 1.84
    try:
        cg = _fetch_coingecko()
        price_real = cg.get("price", 0)
        supply_now = cg.get("supply", 0)
        supply_prev, _ = _fetch_coinmetrics_timeseries("SplyCur", days=365)
    except Exception:
        price_real = 0
        supply_now = 0
        supply_prev = 0

    flow = max(supply_now - supply_prev, 0)
    s2f  = supply_now / flow if flow > 0 else 0
    price_model = math.exp(b) * (s2f ** a) if s2f > 0 else 0
    variance = math.log(price_real / price_model) if price_real > 0 and price_model > 0 else 0

    if variance > 1:
        score = 3
    elif variance > 0:
        score = 2
    elif variance > -1:
        score = 1
    else:
        score = 0

    peso = 0.35
    return {
        "indicador": "Model Variance (S2F)",
        "valor": round(variance, 2),
        "pontuacao_bruta": score,
        "peso": peso,
        "pontuacao_ponderada": round((score / 3) * peso, 4)
    }

def get_mvrv_zscore() -> dict:
    peso = 0.25
    try:
        _, curr = _fetch_coinmetrics_timeseries("MVRV.ZSCORE", days=1)
        value = curr
    except Exception:
        try:
            mk, _ = _fetch_coinmetrics_timeseries("CapMrktCurUSD", days=1)
            rl, _ = _fetch_coinmetrics_timeseries("CapRealUSD", days=1)
            value = mk / rl if rl else 0
        except:
            value = 0

    if value > 3:
        score = 3
    elif value > 1:
        score = 2
    elif value > -1:
        score = 1
    else:
        score = 0

    return {
        "indicador": "MVRV Z-Score",
        "valor": round(value, 2),
        "pontuacao_bruta": score,
        "peso": peso,
        "pontuacao_ponderada": round((score / 3) * peso, 4)
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
