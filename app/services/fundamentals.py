# app/services/fundamentals.py

import math
import requests
import pandas as pd
from datetime import datetime
from requests.exceptions import HTTPError

COINGECKO_URL       = "https://api.coingecko.com/api/v3/coins/bitcoin"
COINGECKO_HISTORY   = "https://api.coingecko.com/api/v3/coins/bitcoin/history"
COINMETRICS_BASE    = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
FRED_M2_CSV         = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=M2SL"


def _fetch_coingecko() -> dict:
    """Retorna dict com 'price' (USD) e 'supply' circulante do BTC."""
    resp = requests.get(
        COINGECKO_URL,
        params={"localization": "false", "tickers": "false", "market_data": "true"}
    )
    resp.raise_for_status()
    data = resp.json().get("market_data", {})
    return {
        "price": data.get("current_price", {}).get("usd", 0),
        "supply": data.get("circulating_supply", 0)
    }


def _fetch_coinmetrics(metric: str) -> float:
    """Busca último valor diário do metric na Community API do CoinMetrics, com parsing robusto."""
    params = {"assets": "btc", "metrics": metric, "frequency": "1d"}
    resp = requests.get(COINMETRICS_BASE, params=params)
    resp.raise_for_status()
    payload = resp.json()
    data = payload.get("data", [])
    if not data:
        raise ValueError(f"No data returned for metric '{metric}'")
    last = data[-1]
    if isinstance(last, dict):
        if "value" in last:
            return float(last["value"])
        if isinstance(last.get("values"), (list, tuple)) and len(last["values"]) >= 2:
            return float(last["values"][1])
        for k, v in last.items():
            if k not in {"time", "asset", "metric", "frequency"}:
                try:
                    return float(v)
                except Exception:
                    continue
        raise ValueError(f"No numeric field found for metric '{metric}'")
    if isinstance(last, (list, tuple)) and len(last) >= 2:
        return float(last[1])
    raise ValueError(f"Unexpected data format for metric '{metric}'")


def get_model_variance() -> dict:
    """
    Calcula Model Variance como ln(P_real / P_model), variando entre -2 e 2.
    P_model = exp(b) * (S2F) ^ a, com a=3.36, b=1.84.
    """
    a, b = 3.36, 1.84

    # dados atuais
    data_now   = _fetch_coingecko()
    price_real = data_now.get("price", 0)
    supply_now = data_now.get("supply", 0)

    # historical supply de um ano atrás
    one_year_ago = (datetime.utcnow() - pd.DateOffset(days=365)).strftime("%d-%m-%Y")
    resp_hist = requests.get(
        COINGECKO_HISTORY,
        params={"date": one_year_ago, "localization": "false"}
    )
    resp_hist.raise_for_status()
    market_data = resp_hist.json().get("market_data", {})
    supply_prev = market_data.get("circulating_supply", 0)

    # calcula S2F
    flow = supply_now - supply_prev if supply_now and supply_prev else 0
    s2f  = supply_now / flow if flow > 0 else 0

    # preço de modelo
    price_model = math.exp(b) * (s2f ** a) if s2f > 0 else 0

    # variância como ln(P_real / P_model)
    variance = math.log(price_real / price_model) if price_model > 0 and price_real > 0 else 0

    # pontuação bruta
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
        value = _fetch_coinmetrics("MVRV.ZSCORE")
        indicador = "MVRV Z-Score"
    except (HTTPError, ValueError):
        mkt_cap      = _fetch_coinmetrics("CapMrktCurUSD")
        realized_cap = _fetch_coinmetrics("CapRealUSD")
        value = (mkt_cap / realized_cap) if realized_cap else 0
        indicador = "MVRV Ratio (Computed)"
    if value > 3:
        score = 3
    elif value > 1:
        score = 2
    elif value > -1:
        score = 1
    else:
        score = 0
    return {
        "indicador": indicador,
        "valor": round(value, 2),
        "pontuacao_bruta": score,
        "peso": peso,
        "pontuacao_ponderada": round((score / 3) * peso, 4)
    }


def get_vdd_multiple() -> dict:
    peso = 0.20
    try:
        value = _fetch_coinmetrics("VDD.Multiple")
        indicador = "VDD Multiple"
    except (HTTPError, ValueError):
        value = 0
        indicador = "VDD Multiple (Unavailable)"
    if value > 3:
        score = 3
    elif value > 1:
        score = 2
    elif value > 0.5:
        score = 1
    else:
        score = 0
    return {
        "indicador": indicador,
        "valor": round(value, 2),
        "pontuacao_bruta": score,
        "peso": peso,
        "pontuacao_ponderada": round((score / 3) * peso, 4)
    }


def get_m2_global_expansion() -> dict:
    df = pd.read_csv(FRED_M2_CSV)
    df["DATE"] = pd.to_datetime(df.iloc[:, 0])
    val_col = df.columns[1]
    series  = df.set_index("DATE")[val_col]
    latest_date = series.index.max()
    latest_val  = series.loc[latest_date]
    six_months_ago = latest_date - pd.DateOffset(months=6)
    prev_slice     = series[series.index <= six_months_ago]
    prev_val       = prev_slice.iloc[-1] if not prev_slice.empty else series.iloc[0]
    pct6m = (latest_val / prev_val - 1) * 100
    if pct6m > 10:
        score = 3
    elif pct6m > 5:
        score = 2
    elif pct6m > 0:
        score = 1
    else:
        score = 0
    peso = 0.20
    return {
        "indicador": "Expansão Global M2 (6m)",
        "valor": round(pct6m, 2),
        "pontuacao_bruta": score,
        "peso": peso,
        "pontuacao_ponderada": round((score / 3) * peso, 4)
    }


def get_all_fundamentals() -> dict:
    lista = [
        get_model_variance(),
        get_mvrv_zscore(),
        get_vdd_multiple(),
        get_m2_global_expansion()
    ]
    total_ponderado = sum(item["pontuacao_ponderada"] for item in lista)
    score_final     = round(total_ponderado * 10, 2)
    return {
        "tabela": lista,
        "consolidado": score_final
    }