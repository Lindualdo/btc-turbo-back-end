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
    
    A resposta inclui:
    - Um score final de risco normalizado (0-10)
    - Classificação qualitativa do risco atual
    - Blocos de risco por categoria (Técnico, Estrutural, Macro, Financeiro)
    - Principais alertas para cada categoria
    - Um resumo executivo com recomendações
    
    Cada bloco de risco informa:
    - Categoria
    - Score de risco
    - Peso na análise final
    - Alertas principais identificados
    """
    try:
        return get_consolidated_risk_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise de risco: {str(e)}")