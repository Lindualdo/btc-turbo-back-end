from fastapi import APIRouter, HTTPException
from app.services.financial_risk_service import FinancialRiskService
from typing import Dict, Any

router = APIRouter()
financial_risk_service = FinancialRiskService()

@router.get("/risco-financeiro", response_model=Dict[str, Any], tags=["Análise de Risco"])
async def get_financial_risk_analysis():
    """
    Análise detalhada do risco financeiro baseado em Health Factor e Alavancagem.
    
    Retorna:
    - Score de risco (0-10)
    - Classificação do risco
    - Detalhes de cada indicador (HF e Alavancagem)
    - Principais alertas
    """
    try:
        # Busca os dados financeiros via scraping
        financial_data = await financial_risk_service.fetch_financial_data()
        
        # Calcula o risco financeiro
        risk_analysis = financial_risk_service.calculate_financial_risk(financial_data)
        
        return risk_analysis
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao analisar risco financeiro: {str(e)}"
        )