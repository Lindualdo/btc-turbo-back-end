from fastapi import APIRouter, HTTPException, Depends
from app.services.risk_analysis_trend import calculate_trend_risk
from app.config import Settings, get_settings
from typing import Dict, Any

router = APIRouter()

@router.get("/analise-tendencia-risco", 
              summary="Análise de Risco de Tendência", 
              tags=["Análise Técnica"])
def get_trend_risk_analysis(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    """
    Retorna análise de risco baseada na força da tendência.
    
    A análise inverte o score técnico das EMAs para obter uma medida de risco:
    Risco = 10 - Score de Força da Tendência
    
    Exemplo:
    - Score EMAs 9,0 = Risco 1,0 (Baixo)
    - Score EMAs 2,5 = Risco 7,5 (Alto)
    
    Returns:
        Dict: Análise detalhada do risco de tendência com classificação e alertas
    """
    try:
        result = calculate_trend_risk()
        
        # Adicionar explicação da classificação de risco baseada na pontuação
        risk_level = result.get("pontuacao", 0)
        
        # Incluindo o score de força original da API analise-tecnica-emas
        result["score_forca_tendencia"] = result.get("detalhes", {}).get("score_forca_original", 0)
        
        risk_classification = {
            "risco": round(risk_level, 1),
            "classificacao": result.get("classificacao", "Indeterminado"),
            "tabela_referencia": [
                {"nivel": "0.0 - 1.9", "alerta": "✅ Nenhum", "interpretacao": "Estrutura técnica totalmente saudável", "recomendacao": "Seguir plano normalmente"},
                {"nivel": "2.0 - 3.9", "alerta": "⚠️ Monitorar", "interpretacao": "Pequenos sinais de fraqueza", "recomendacao": "Aumentar atenção / avaliar exposição"},
                {"nivel": "4.0 - 5.9", "alerta": "🟠 Alerta Moderado", "interpretacao": "Estrutura comprometida em múltiplos TFs", "recomendacao": "Reduzir risco / avaliar colateral"},
                {"nivel": "6.0 - 7.9", "alerta": "🔴 Alerta Crítico", "interpretacao": "Alta probabilidade de reversão", "recomendacao": "Desalavancar / proteger posição"},
                {"nivel": "8.0 - 10.0", "alerta": "🚨 Alerta Máximo", "interpretacao": "Colapso técnico estrutural", "recomendacao": "Fechar alavancagem / modo defesa total"}
            ]
        }
        
        result["classificacao_detalhada"] = risk_classification
        
        # Adicionar interpretação baseada no nível atual
        for nivel in risk_classification["tabela_referencia"]:
            faixa = nivel["nivel"].split(" - ")
            min_val = float(faixa[0])
            max_val = float(faixa[1])
            
            if min_val <= risk_level <= max_val:
                result["interpretacao_atual"] = {
                    "alerta": nivel["alerta"],
                    "interpretacao": nivel["interpretacao"],
                    "recomendacao": nivel["recomendacao"]
                }
                break
                
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular risco de tendência: {str(e)}")