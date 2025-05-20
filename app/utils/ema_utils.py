# app/utils/ema_utils.py

import pandas as pd

def calcular_emas(df: pd.DataFrame, periods: list[int]) -> pd.DataFrame:
    for period in periods:
        df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    return df

def analisar_timeframe(preco, emas):
    pesos_alinhamento = {
        ("EMA_17", "EMA_34"): 1,
        ("EMA_34", "EMA_144"): 2,
        ("EMA_144", "EMA_305"): 3,
        ("EMA_305", "EMA_610"): 4,
    }

    pesos_preco = {
        "EMA_17": 1,
        "EMA_34": 1,
        "EMA_144": 2,
        "EMA_305": 3,
        "EMA_610": 3,
    }

    pontos_ema = 0
    pontos_preco = 0
    observacoes = []

    # Alinhamento das EMAs
    for (mais_rapida, mais_lenta), peso in pesos_alinhamento.items():
        if emas[mais_rapida] > emas[mais_lenta]:
            pontos_ema += peso
        else:
            observacoes.append(f"{mais_rapida} abaixo da {mais_lenta}")

    # Posição do preço
    for ema, peso in pesos_preco.items():
        if preco > emas[ema]:
            pontos_preco += peso
        else:
            observacoes.append(f"preço abaixo da {ema}")

    score_raw = pontos_ema + pontos_preco
    score = round((score_raw / 20) * 10, 1)

    if score >= 8.1:
        classificacao = "Tendência de Alta muito forte"
    elif score >= 6.1:
        classificacao = "Tendência de Alta forte"
    elif score >= 4.1:
        classificacao = "Tendência de Alta moderada"
    elif score >= 2.1:
        classificacao = "Tendência de alta fraca"
    else:
        classificacao = "Final da tendêcia de Alta"

    observacao = ", ".join(observacoes) if observacoes else "cenário ideal: preço acima e EMAs alinhadas"

    return {
        "score": score,
        "classificacao": classificacao,
        "observacao": observacao
    }

def consolidar_scores(scores_dict):
    pesos = {
        "1w": 0.5,
        "1d": 0.25,
        "4h": 0.15,
        "1h": 0.10
    }
    total = 0.0
    racional_partes = []

    for tf, peso in pesos.items():
        score = scores_dict.get(tf, {}).get("score", 0)
        total += score * peso
        racional_partes.append(f"(score_{tf}: {score} * {peso})")

    score_final = round(total, 1)

    if score >= 8.1:
        classificacao = "Tendência de Alta muito forte"
    elif score >= 6.1:
        classificacao = "Tendência de Alta forte"
    elif score >= 4.1:
        classificacao = "Tendência de Alta moderada"
    elif score >= 2.1:
        classificacao = "Tendência de alta fraca"
    else:
        classificacao = "Final da tendêcia de Alta"

    return {
        "score": score_final,
        "classificacao": classificacao,
        "racional": "score_final = " + " + ".join(racional_partes)
    }
