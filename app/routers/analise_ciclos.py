from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.services.btc_analysis import analyze_btc_cycles
from app.dependencies import get_tv_client
from tvDatafeed import TvDatafeed

router = APIRouter()

@router.get("/analise-ciclos", 
            summary="Análise de Ciclos do BTC", 
            tags=["Ciclos"])
async def analise_ciclos(
    username: Optional[str] = Query(None, description="TradingView username"),
    password: Optional[str] = Query(None, description="TradingView password"),
    tv: TvDatafeed = Depends(get_tv_client)
):
    """
    Análise quantitativa de ciclos do BTC v2.0
    
    Indicadores:
    - BTC vs EMA 200D (30%)
    - BTC vs Realized Price (30%) 
    - Puell Multiple (20%)
    - M2 Growth (15%)
    - Funding Rates 7D (5%)
    
    Retorna score 0-10 com classificação Bull/Bear.
    """
    try:
        resultado = analyze_btc_cycles(tv)
        return resultado
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro na análise de ciclos: {str(e)}"
        )