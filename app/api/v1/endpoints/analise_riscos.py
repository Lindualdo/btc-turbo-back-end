from fastapi import APIRouter, HTTPException
from app.services.financial_risk_service import FinancialRiskService
from typing import Dict, Any

router = APIRouter()
financial_risk_service = FinancialRiskService()

@router.get("/analise-riscos", response_model=Dict[str, Any], tags=["Análise de Risco"])
async def get_risk_analysis():
    """
    Análise consolidada de risco com todas as categorias.
    
    Retorna:
    - Risco final consolidado
    - Blocos de risco por categoria
    - Resumo com principais alertas
    """
    try:
        # Obter dados de risco financeiro
        financial_data = await financial_risk_service.fetch_financial_data()
        financial_risk = financial_risk_service.calculate_financial_risk(financial_data)
        
        # Simular riscos de outras categorias (a serem implementados no futuro)
        technical_risk = {
            "categoria": "Técnico",
            "score": 3.4,
            "peso": 0.15,
            "principais_alertas": [
                "Falta alinhamento EMAs 4H e Intradays",
                "Divergência bearish no RSI detectada no 4h"
            ]
        }
        
        structural_risk = {
            "categoria": "Estrutural BTC",
            "score": 2.5,
            "peso": 0.2,
            "principais_alertas": [
                "Fundamentos esticados",
                "Fear & Greed: 87 (ganância)"
            ]
        }
        
        macro_risk = {
            "categoria": "Macro & Plataforma",
            "score": 1.0,
            "peso": 0.3,
            "principais_alertas": [
                "Ouro em alta forte"
            ]
        }
        
        # Lista de todos os blocos de risco
        risk_blocks = [
            financial_risk,
            technical_risk,
            structural_risk,
            macro_risk
        ]
        
        # Cálculo do risco final ponderado
        final_score = sum(block["score"] * block["peso"] for block in risk_blocks)
        final_score = round(final_score, 2)
        
        # Determinar classificação do risco final
        classification, description = get_risk_classification(final_score)
        
        # Identificar componentes de maior risco (para o resumo)
        sorted_blocks = sorted(risk_blocks, key=lambda x: x["score"] * x["peso"], reverse=True)
        high_risk_components = [block["categoria"] for block in sorted_blocks[:2]]
        
        # Construir a resposta
        response = {
            "risco_final": {
                "score": final_score,
                "classificacao": classification,
                "descricao": description
            },
            "blocos_risco": risk_blocks,
            "resumo": {
                "alerta": f"Monitorar componentes com maior peso de risco: {' e '.join(high_risk_components)}."
            }
        }
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao analisar riscos: {str(e)}"
        )

def get_risk_classification(score):
    """Determina a classificação e descrição do risco com base no score final"""
    if score < 2.0:
        return "✅ Risco Mínimo", "Cenário favorável, baixo risco operacional."
    elif score < 4.0:
        return "✅ Risco Controlado", "Risco administrável, monitorar regularmente."
    elif score < 6.0:
        return "⚠️ Risco Moderado", "Atenção necessária, revisar alavancagem."
    elif score < 8.0:
        return "🚨 Risco Elevado", "Reduzir exposição, ajustar estratégia."
    else:
        return "⛔ Risco Crítico", "Situação de alto risco, considerar redução imediata."