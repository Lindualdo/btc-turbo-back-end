from fastapi import APIRouter
from tvDatafeed import TvDatafeed
from app.services.btc_analysis import get_btc_vs_200d_ema, get_realized_price_vs_price_atual

router = APIRouter()

@router.get("/btc-cycles")
def btc_cycles(username: str, password: str):
    tv = TvDatafeed(username=username, password=password)
    indicador1 = get_btc_vs_200d_ema(tv)
    indicador2 = get_realized_price_vs_price_atual(tv)

    dados = [indicador1, indicador2]
    total_ponderado = sum(item["pontuacao_ponderada"] for item in dados)
    pontuacao_final = round((total_ponderado / 2.0) * 10, 2)

    faixas = [
        (8.1, 10.0, "🟢 Bull Forte", "Operar agressivamente"),
        (6.1, 8.0, "🔵 Bull Moderado", "Tamanho controlado"),
        (4.1, 6.0, "🟡 Tendência Neutra", "Pouca exposição"),
        (2.1, 4.0, "🟠 Bear Leve", "Atenção / Exposição mínima"),
        (0.0, 2.0, "🔴 Bear Forte", "Defesa máxima (sem novas entradas)")
    ]

    for min_val, max_val, classificacao, estrategia in faixas:
        if min_val <= pontuacao_final <= max_val:
            classificacao_final = classificacao
            estrategia_final = estrategia
            break

    destaques = []
    for item in dados:
        if item["pontuacao_bruta"] == 2:
            destaques.append(f"🔹 {item['indicador']} está forte")
        elif item["pontuacao_bruta"] == 0:
            destaques.append(f"⚠️ {item['indicador']} está fraco")

    return {
        "dados_individuais": dados,
        "pontuacao_final": pontuacao_final,
        "classificacao": classificacao_final,
        "estrategia": estrategia_final,
        "resumo_executivo": destaques
    }