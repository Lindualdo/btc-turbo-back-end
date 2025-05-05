# app/services/fundamentals.py

import math
import requests
import pandas as pd
from datetime import datetime
from requests.exceptions import HTTPError

COINGECKO_URL    = "https://api.coingecko.com/api/v3/coins/bitcoin"
COINMETRICS_BASE = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
FRED_M2_CSV      = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=M2SL"


def _fetch_coingecko() -> dict:
    """Retorna dict com 'price' (USD) e 'supply' circulante do BTC."""
    resp = requests.get(
        COINGECKO_URL,
        params={"localization": "false", "tickers": "false", "market_data": "true"}
    )
    resp.raise_for_status()
    data = resp.json()["market_data"]
    return {
        "price": data["current_price"]["usd"],
        "supply": data["circulating_supply"]
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
        raise KeyError("value")
    if isinstance(last, (list, tuple)) and len(last) >= 2:
        return float(last[1])
    raise KeyError("value")


def get_model_variance() -> dict:
    """
    Calcula Stock-to-Flow (S2F) e Model Variance em porcentagem.
    Usa parâmetros PlanB originais: slope=3.36, intercept=+0.799 (log10).
    Retorna dicionário com indicador, valor (%), pontuacao_bruta, peso e pontuacao_ponderada.
    """
    # parâmetros públicos PlanB: log10(P) = a·log10(S2F) + b
    a, b = 3.36, 0.799

    data   = _fetch_coingecko()
    supply = data["supply"]
    price  = data["price"]

    # estimativa de flow anual (pós-halving): 3.125 BTC/bloco * 6 blocos/h * 24h * 365 ≈ 164250 BTC/ano
    flow = 3.125 * 6 * 24 * 365
    s2f  = supply / flow

    # calcula preço de modelo e variância em %
    price_s2f = 10 ** (a * math.log10(s2f) + b)
    variance_pct = (price - price_s2f) / price_s2f * 100

    # pontuação bruta: thresholds baseados em %
    if variance_pct > 100:
        score = 3
    elif variance_pct > 0:
        score = 2
    elif variance_pct > -100:
        score = 1
    else:
        score = 0

    peso = 0.35
    return {
        "indicador": "Model Variance (S2F)",
        "valor": round(variance_pct, 2),
        "pontuacao_bruta": score,
        "peso": peso,
        "pontuacao_ponderada": round((score / 3) * peso, 4)
    }


def get_mvrv_zscore() -> dict:
    peso = 0.25
    try:
        value = _fetch_coinmetrics("MVRV.ZSCORE")
        indicador = "MVRV Z-Score"
    except HTTPError as err:
        if err.response.status_code == 400:
            mkt_cap      = _fetch_coinmetrics("CapMrktCurUSD")
            realized_cap = _fetch_coinmetrics("CapRealUSD")
            value = (mkt_cap / realized_cap) if realized_cap else 0
            indicador = "MVRV Ratio (Computed)"
        else:
            raise
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
    except HTTPError as err:
        if err.response.status_code == 400:
            value = 0
            indicador = "VDD Multiple (Unavailable)"
        else:
            raise
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
