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


def get_model_variance() -> dict:
    """
    Calcula Stock-to-Flow e Model Variance usando fórmula S2F de PlanB.
    Retorna:
      indicador, valor (variance), pontuacao_bruta, peso, pontuacao_ponderada.
    """
    a, b = 3.36, -1.8  # parâmetros públicos PlanB

    data   = _fetch_coingecko()
    supply = data["supply"]
    price  = data["price"]

    flow = 6.25 * 6 * 24 * 365
    s2f  = supply / flow

    price_s2f = 10 ** (a * math.log10(s2f) + b)
    variance  = (price - price_s2f) / price_s2f

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
        "valor": variance,
        "pontuacao_bruta": score,
        "peso": peso,
        "pontuacao_ponderada": (score / 3) * peso
    }


def _fetch_coinmetrics(metric: str) -> float:
    """Busca último valor diário do metric na Community API do CoinMetrics."""
    params = {
        "assets": "btc",
        "metrics": metric,
        "frequency": "1d",
    }
    resp = requests.get(COINMETRICS_BASE, params=params)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    return float(data[-1]["value"])


def get_mvrv_zscore() -> dict:
    """
    Tenta buscar MVRV Z-Score; se não suportado (400), faz fallback para MVRV.Ratio.
    Retorna dict com indicador, valor, pontuacao_bruta, peso e pontuacao_ponderada.
    """
    peso = 0.25

    try:
        # primeira tentativa: Z-Score
        value = _fetch_coinmetrics("MVRV.ZSCORE")
        indicador = "MVRV Z-Score"
    except HTTPError as err:
        if err.response.status_code == 400:
            # fallback para ratio
            value = _fetch_coinmetrics("MVRV.Ratio")
            indicador = "MVRV Ratio (Fallback)"
        else:
            # re-lança outros erros de HTTP
            raise

    # cálculo da pontuação bruta
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
        "valor": value,
        "pontuacao_bruta": score,
        "peso": peso,
        "pontuacao_ponderada": (score / 3) * peso
    }


def get_vdd_multiple() -> dict:
    """Retorna VDD Multiple com pontuação e peso."""
    value = _fetch_coinmetrics("VDD.Multiple")

    if value > 3:
        score = 3
    elif value > 1:
        score = 2
    elif value > 0.5:
        score = 1
    else:
        score = 0

    peso = 0.20
    return {
        "indicador": "VDD Multiple",
        "valor": value,
        "pontuacao_bruta": score,
        "peso": peso,
        "pontuacao_ponderada": (score / 3) * peso
    }


def get_m2_global_expansion() -> dict:
    """
    Lê CSV do FRED (M2 EUA) e calcula expansão percentual nos últimos 6 meses.
    """
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
        "valor": pct6m,
        "pontuacao_bruta": score,
        "peso": peso,
        "pontuacao_ponderada": (score / 3) * peso
    }


def get_all_fundamentals() -> dict:
    """
    Gera tabela com todos os indicadores e calcula pontuação final 0–10.
    """
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
