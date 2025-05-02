from fastapi import APIRouter
from datetime import datetime
from tvDatafeed import TvDatafeed
from app.services.btc_analysis import (
    get_btc_vs_200d_ema,
    get_realized_price_vs_price_atual,
    get_puell_multiple as get_puell_multiple_from_notion,
    get_btc_dominance_tendencia,
    get_juros_tendencia,
    get_expansao_global_from_notion
)

router = APIRouter()

def consolidar_macro_ambiente(juros: dict, expansao: dict) -> dict:
    try:
        pontos_juros = juros.get("pontuacao_bruta", 0)
        pontos_expansao = expansao.get("pontuacao_bruta", 0)

        peso_juros = 0.40
        peso_expansao = 0.60

        pontuacao_final = round((pontos_juros * peso_juros) + (pontos_expansao * peso_expansao), 2)

        if pontuacao_final >= 1.5:
            classificacao = "Expansivo"
        elif pontuacao_final >= 0.75:
            classificacao = "Neutro"
        else:
            classificacao = "Restritivo"

        return {
            "indicador": "Macro Ambiente",
            "fonte": "Cálculo consolidado (Expansão Global + Juros)",
            "pontuacao_bruta": pontuacao_final,
            "peso": 0.10,
            "pontuacao_ponderada": round(pontuacao_final * 0.10, 2),
            "classificacao": classificacao
        }

    except Exception as e:
        return {
            "indicador": "Macro Ambiente",
            "fonte": "Cálculo consolidado (Expansão Global + Juros)",
            "pontuacao_bruta": 0.0,
            "peso": 0.10,
            "pontuacao_ponderada": 0.0,
            "classificacao": "Erro",
            "erro": str(e)
        }

@router.get("/btc-cycles")
def btc_cycles(username: str, password: str):
    tv = TvDatafeed(username=username, password=password)

    ema = get_btc_vs_200d_ema(tv)
    realized = get_realized_price_vs_price_atual(tv)
    puell = get_puell_multiple_from_notion()
    dominancia = get_btc_dominance_tendencia(tv)
    juros = get_juros_tendencia(tv)
    expansao = get_expansao_global_from_notion()
    macro = consolidar_macro_ambiente(juros, expansao)

    indicadores = [
        ema,
        realized,
        puell,
        dominancia,
        juros,
        expansao,
        macro
    ]

    pesos_personalizados = {
        "BTC vs 200D EMA": 0.25,
        "BTC vs Realized Price": 0.25,
        "Puell Multiple": 0.20,
        "BTC Dominance Tendência": 0.20,
        "Macro Ambiente": 0.10,
        "Juros (US10Y - 90d)": 0.0,
        "Expansão Global": 0.0
    }

    for i in indicadores:
        peso = pesos_personalizados.get(i["indicador"], i.get("peso", 0))
        i["peso"] = peso
        i["pontuacao_ponderada"] = round(i["pontuacao_bruta"] * peso, 2)

    total_ponderado = sum(i["pontuacao_ponderada"] for i in indicadores)
    pontuacao_final = round((total_ponderado / 2.0) * 10, 2)

    faixas = [
        (8.1, 10.0, "🟢 Bull Forte", "Operar agressivamente"),
        (6.1, 8.0, "🔵 Bull Moderado", "Tamanho controlado"),
        (4.1, 6.0, "🟡 Tendência Neutra", "Pouca exposição"),
        (2.1, 4.0, "🟠 Bear Leve", "Exposição mínima"),
        (0.0, 2.0, "🔴 Bear Forte", "Defesa máxima")
    ]

    classificacao_final = "Indefinida"
    estrategia_final = "Sem estratégia"

    for min_val, max_val, classificacao, estrategia in faixas:
        if min_val <= pontuacao_final <= max_val:
            classificacao_final = classificacao
            estrategia_final = estrategia
            break

    destaques = []
    for i in indicadores:
        if i["pontuacao_bruta"] == 2:
            destaques.append(f"🔹 {i['indicador']} está forte")
        elif i["pontuacao_bruta"] == 0:
            destaques.append(f"⚠️ {i['indicador']} está fraco")
        elif "variacao_pct" in i and i["variacao_pct"] is not None:
            destaques.append(f"ℹ️ {i['indicador']} variou {i['variacao_pct']}%")

    return {
        "dados_individuais": indicadores,
        "dados_consolidados": {
            "pontuacao_final": pontuacao_final,
            "classificacao": classificacao_final,
            "estrategia": estrategia_final,
            "data_processamento": datetime.utcnow().isoformat() + "Z"
        },
        "resumo_executivo": destaques
    }
