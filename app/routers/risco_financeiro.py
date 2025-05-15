from fastapi import APIRouter, HTTPException
from app.services.financial_risk_service import FinancialRiskService
import asyncio

router = APIRouter()
financial_risk_service = FinancialRiskService()

@router.get(
    "/risco-financeiro", 
    summary="Análise de Risco Financeiro dos Indicadores DeFi",
    tags=["Análise de Risco"]
)
async def get_financial_risk_analysis():
    """
    Análise detalhada do risco financeiro baseado em Health Factor e Alavancagem.
    
    Os dados são obtidos via scraping da plataforma DeFiSim para a carteira monitorada.
    
    Retorna:
    - Score de risco (0-10)
    - Classificação do risco
    - Detalhes de cada indicador (HF e Alavancagem)
    - Principais alertas identificados
    
    O Health Factor (HF) é um indicador crítico que representa a saúde da 
    posição alavancada. Valores abaixo de 1.5 representam riscos significativos.
    
    A Alavancagem é calculada dividindo "Supplied Asset Value" por "Net Asset Value".
    Valores acima de 3.0 são considerados elevados.
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