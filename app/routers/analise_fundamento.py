# app/routers/analise_tecnica_emas.py
# app/routers/analise_fundamentos.py

from fastapi import APIRouter, HTTPException, Depends
from app.services.tv_session_manager import get_tv_instance
from app.config import Settings, get_settings
from app.services.btc_analysis import (
    get_realized_price_vs_price_atual,
    get_puell_multiple as get_puell_multiple_from_notion,
    get_expansao_global_from_notion
)

router = APIRouter()

@router.get(
    "/analise-fundamentos",
    summary="Análise de Fundamentos On-Chain do BTC",
    tags=["Fundamentos On-Chain"]
)
def analise_fundamentos(settings: Settings = Depends(get_settings)):
    """
    Retorna a análise dos principais indicadores on-chain:
    - BTC vs Realized Price
    - Puell Multiple
    - Expansão Global
    """
    try:
        # Instância de sessão TradingView, se necessária em algum indicador
        tv = get_tv_instance()

        # Chama serviços de análise on-chain
        realized = get_realized_price_vs_price_atual(tv)
        puell = get_puell_multiple_from_notion()
        expansao = get_expansao_global_from_notion()

        return {
            "indicadores": [
                realized,
                puell,
                expansao
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise de fundamentos: {str(e)}")
