# app/routers/analise_fundamentos.py

from fastapi import APIRouter, HTTPException
from app.services.fundamentals import get_all_fundamentals

router = APIRouter()

@router.get(
    "/analise-fundamentos",
    summary="Análise Fundamentalista On-Chain do BTC",
    tags=["Fundamentos On-Chain"]
)
def analise_fundamentos():
    """
    Retorna a análise fundamentalista completa de indicadores on-chain:
    - Model Variance (S2F)
    - MVRV Z-Score
    - VDD Multiple
    - Expansão Global M2 (6m)
    """
    try:
        return get_all_fundamentals()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise de fundamentos: {str(e)}")
