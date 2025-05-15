import logging
import requests
from typing import Dict, Any
from app.config import get_settings

def calculate_trend_risk() -> Dict[str, Any]:
    """
    Calcula o componente de risco de tendência para análise de risco técnico.
    
    Inverte a lógica da pontuação do endpoint de EMAs (quanto maior o score EMAs, 
    menor o risco de tendência). Normaliza para uma escala de 0-10 para risco.
    
    Pontuação máxima: 10 pontos
    """
    try:
        settings = get_settings()
        base_url = f"http://localhost:{settings.PORT}/api/v1"
        
        # Consultar o endpoint de análise de EMAs
        response = requests.get(f"{base_url}/analise-tecnica-emas")
        if response.status_code != 200:
            logging.error(f"Erro ao consultar endpoint de EMAs: {response.status_code}")
            # Retornar objeto padrão em caso de erro
            return default_trend_risk_response("Erro ao consultar dados de EMAs")
            
        data = response.json()
        consolidado = data.get("consolidado", {})
        score_emas = consolidado.get("score", 0.0)
        
        # Inverter a lógica (10 - score)
        # Score 9.5 (força alta) = risco 0.5 (risco baixo)
        # Score 2.0 (força baixa) = risco 8.0 (risco alto)
        trend_risk_score = 10.0 - score_emas if score_emas <= 10 else 0
        
        # Classificar o risco conforme a pontuação
        risk_classification = classify_trend_risk(trend_risk_score)
        
        # Extrair dados relevantes para análise
        timeframe_scores = {}
        for tf, data in data.get("emas", {}).items():
            if "analise" in data and "score" in data["analise"]:
                timeframe_scores[tf] = {
                    "score_forca": data["analise"]["score"],
                    "score_risco": 10.0 - data["analise"]["score"],
                    "alinhamento": data["analise"].get("alinhamento", "N/A"),
                    "posicao_preco": data["analise"].get("posicao_preco", "N/A")
                }
        
        # Gerar descrição do risco e alertas
        alertas = []
        
        if trend_risk_score >= 8:
            alertas.append("🚨 Colapso técnico estrutural - tendência extremamente fraca")
        elif trend_risk_score >= 6:
            alertas.append("🔴 Alta probabilidade de reversão - estrutura técnica comprometida")
        elif trend_risk_score >= 4:
            alertas.append("🟠 Estrutura técnica comprometida em múltiplos timeframes")
        elif trend_risk_score >= 2:
            alertas.append("⚠️ Pequenos sinais de fraqueza técnica - monitorar")
        
        # Adicionar informações específicas sobre EMAs problemáticas
        if "1w" in timeframe_scores and timeframe_scores["1w"]["score_risco"] > 5:
            alertas.append(f"EMAs semanais mostrando fraqueza significativa (risco: {timeframe_scores['1w']['score_risco']:.1f})")
            
        if "1d" in timeframe_scores and timeframe_scores["1d"]["score_risco"] > 5:
            alertas.append(f"EMAs diárias mostrando fraqueza (risco: {timeframe_scores['1d']['score_risco']:.1f})")
            
        # Se não houver alertas específicos, adicionar mensagem padrão
        if not alertas:
            alertas = ["✅ Estrutura técnica totalmente saudável - tendência forte"]
            
        # Montar racional da análise
        racional = []
        for tf in ["1w", "1d", "4h", "1h", "15m"]:
            if tf in timeframe_scores:
                racional.append(f"{tf}: Score {timeframe_scores[tf]['score_forca']:.1f} (risco {timeframe_scores[tf]['score_risco']:.1f})")
        
        return {
            "componente": "Análise de Tendência",
            "pontuacao": round(trend_risk_score, 2),
            "pontuacao_maxima": 10.0,
            "classificacao": risk_classification,
            "timeframes": timeframe_scores,
            "alertas": alertas,
            "racional": ", ".join(racional),
            "detalhes": {
                "score_forca_original": score_emas,
                "metodologia": "Inversão do score de força (10 - score_força)"
            }
        }
    except Exception as e:
        logging.error(f"Erro ao calcular risco de tendência: {str(e)}")
        return default_trend_risk_response(f"Erro: {str(e)}")

def classify_trend_risk(risk_score: float) -> str:
    """
    Classifica o risco de tendência com base na pontuação
    
    Args:
        risk_score: Pontuação de risco (0-10)
        
    Returns:
        String com classificação do risco
    """
    if risk_score < 2:
        return "Nenhum"
    elif risk_score < 4:
        return "Monitorar"
    elif risk_score < 6:
        return "Alerta Moderado"
    elif risk_score < 8:
        return "Alerta Crítico"
    else:
        return "Alerta Máximo"

def default_trend_risk_response(error_msg: str) -> Dict[str, Any]:
    """
    Retorna resposta padrão para caso de falha na análise
    
    Args:
        error_msg: Mensagem de erro
        
    Returns:
        Dicionário com resposta padrão
    """
    return {
        "componente": "Análise de Tendência",
        "pontuacao": 0.0,
        "pontuacao_maxima": 10.0,
        "classificacao": "Indeterminado",
        "timeframes": {},
        "alertas": [f"Não foi possível calcular o risco de tendência: {error_msg}"],
        "racional": "Dados insuficientes para análise",
        "detalhes": {
            "erro": error_msg
        }
    }