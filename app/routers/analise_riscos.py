# app/routers/analise_riscos.py

from fastapi import APIRouter, HTTPException
from app.services.risk_analysis import get_consolidated_risk_analysis

router = APIRouter()

@router.get(
    "/analise-riscos",
    summary="Análise de Risco Consolidada para BTC",
    tags=["Análise de Risco"]
)
def analise_riscos():
    """
    Retorna a análise de risco consolidada para operações de hold alavancado de Bitcoin:
    
    - Risco Técnico (EMAs, IFR, Divergência IFR)
    - Risco Estrutural BTC (Model Variance, MVRV, VDD, Fear & Greed)
    - Risco Macroeconômico e Plataforma (MOVE, DXY, VIX, US10Y, Ouro, M2, Eventos Críticos)
    - Risco Financeiro Direto (Health Factor, Alavancagem, WBTC Supply/Paridade)
    
    A pontuação final é normalizada em escala 0-10, com classificação de risco.
    """
    try:
        return get_consolidated_risk_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise de risco: {str(e)}")