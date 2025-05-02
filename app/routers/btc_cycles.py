from fastapi import APIRouter
from tvDatafeed import TvDatafeed
from app.services.btc_analysis import (
    get_btc_vs_200d_ema,
    get_realized_price_vs_price_atual,
    get_puell_multiple as get_puell_multiple_from_notion,
    get_btc_dominance_mock,
    get_macro_environment_mock
)

router = APIRouter()

@router.get("/btc-cycles")
def btc_cycles(username: str, password: str):
    tv = TvDatafeed(username=username, password=password)

    indicadores = [
        get_btc_vs_200d_ema(tv),
        get_realized_price_vs_price_atual(tv),
        get_puell_multiple_from_notion(),  # agora corretamente do Notion
        get_btc_dominance_mock(),
        get_macro_environment_mock()
    ]

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

    return {
        "dados_individuais": indicadores,
        "dados_consolidados": {
            "pontuacao_final": pontuacao_final,
            "classificacao": classificacao_final,
            "estrategia": estrategia_final
        },
        "resumo_executivo": destaques
    }
