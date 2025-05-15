import logging
from typing import Dict, List, Any, Tuple
from app.services.risk_analysis_rsi import calculate_rsi_risk
from app.services.risk_analysis_divergencia import calculate_divergence_risk
from app.services.risk_analysis_trend import calculate_trend_risk

def calculate_technical_risk() -> Dict[str, Any]:
    """
    Calcula o risco técnico com base em EMAs, IFR e Divergências por timeframe.
    
    Pontuação máxima: 25 pontos
    Peso na ponderação estratégica: 0.15
    """
    # Calcular o componente de risco de RSI (sobrecompra)
    rsi_risk_component = calculate_rsi_risk()
    
    # Calcular o componente de risco de divergências RSI
    divergence_risk_component = calculate_divergence_risk()
    
    # Calcular o componente de risco de tendência (baseado em EMAs)
    trend_risk_component = calculate_trend_risk()
    
    # Valores fixos para teste dos outros componentes
    emas_risk = {
        "1W": 0.0,  # +2.0 se fraco
        "1D": 0.0,  # +1.5 se fraco
        "4H": 0.0,  # +1.0 se fraco
        "intraday": 0.5    # +0.5 se fraco (1H/30M/15M)
    }
    
    # Soma pontuações de todos os indicadores
    total_emas = sum(emas_risk.values())
    total_rsi_overbought = rsi_risk_component["pontuacao"]
    total_rsi_divergence = divergence_risk_component["pontuacao"]
    total_trend_risk = trend_risk_component["pontuacao"]
    
    raw_score = total_emas + total_rsi_overbought + total_rsi_divergence + total_trend_risk
    
    # Criar alertas para os riscos detectados
    alerts = []
    
    # Alertas para EMAs
    if total_emas > 0:
        if emas_risk["4H"] > 0 or emas_risk["intraday"] > 0:
            alerts.append("Falta alinhamento EMAs 4H e Intradays")
        else:
            alerts.append("Falta alinhamento EMAs em timeframes maiores")
    
    # Adicionar alertas do RSI
    alerts.extend(rsi_risk_component["alertas"])
    
    # Adicionar alertas de divergências
    alerts.extend(divergence_risk_component["alertas"])
    
    # Adicionar alertas de tendência
    alerts.extend(trend_risk_component["alertas"])
    
    # Componentes da análise técnica
    componentes = [
        {
            "nome": "Alinhamento EMAs",
            "pontuacao": round(total_emas, 2),
            "pontuacao_maxima": 5.0,
            "valores": emas_risk,
            "racional": "Análise qualitativa baseada na orientação e disposição das EMAs"
        },
        rsi_risk_component,
        divergence_risk_component,
        trend_risk_component
    ]
    
    # Incluir dados consolidados dos indicadores de risco técnico
    indicadores_tecnicos = {
        "rsi_sobrecompra": {
            "pontuacao": total_rsi_overbought,
            "pontuacao_maxima": rsi_risk_component["pontuacao_maxima"],
            "valores": rsi_risk_component.get("valores", {})
        },
        "divergencia_rsi": {
            "pontuacao": total_rsi_divergence,
            "pontuacao_maxima": divergence_risk_component["pontuacao_maxima"],
            "divergencias": divergence_risk_component.get("divergencias_detectadas", {})
        },
        "risco_tendencia": {
            "pontuacao": total_trend_risk,
            "pontuacao_maxima": trend_risk_component["pontuacao_maxima"],
            "score_forca_tendencia": trend_risk_component.get("detalhes", {}).get("score_forca_original", 0)
        }
    }
    
    return {
        "categoria": "Risco Técnico",
        "pontuacao": round(raw_score, 1),
        "max_pontuacao": 25.0,  # Atualizado para incluir o componente de tendência (10 pts)
        "peso": 0.15,
        "pontuacao_ponderada": round(raw_score * 0.15, 2),
        "alertas": alerts if alerts else ["Sem alertas técnicos"],
        "componentes": componentes,
        "indicadores_tecnicos": indicadores_tecnicos  # Novo campo consolidado
    }

def calculate_btc_structural_risk() -> Dict[str, Any]:
    """
    Calcula o risco estrutural do BTC com base em fundamentos e Fear & Greed.
    
    Pontuação máxima: 6 pontos
    Peso na ponderação estratégica: 0.20
    """
    # Valores fixos para teste inicial
    fundamental_models_risk = 1.0  # Max +3 pontos (Model Variance, MVRV, VDD)
    fear_greed_risk = 1.5  # Max +3 pontos (Escala progressiva 80-100)
    
    raw_score = fundamental_models_risk + fear_greed_risk
    
    # Criar alertas para os riscos detectados
    alerts = []
    if fundamental_models_risk > 0:
        alerts.append("Fundamentos esticados")
    
    if fear_greed_risk > 0:
        alerts.append("Fear & Greed em território de ganância (87)")
    
    return {
        "categoria": "Risco Estrutural BTC",
        "pontuacao": round(raw_score, 1),
        "max_pontuacao": 6.0,
        "peso": 0.20,
        "pontuacao_ponderada": round(raw_score * 0.20, 2),
        "alertas": alerts if alerts else ["Fundamentos normais, Fear & Greed neutro"]
    }

def calculate_macro_platform_risk() -> Dict[str, Any]:
    """
    Calcula o risco macroeconômico e de plataforma.
    
    Pontuação máxima: 11 pontos
    Peso na ponderação estratégica: 0.30
    """
    # Valores fixos para teste inicial
    macro_risk = 1.0  # Max +6 pontos (MOVE, DXY, VIX, US10Y, Ouro, M2)
    platform_risk = 0.0  # Max +5 pontos (Eventos críticos AAVE, ETH, USDC)
    
    raw_score = macro_risk + platform_risk
    
    # Criar alertas para os riscos detectados
    alerts = []
    if macro_risk > 0:
        alerts.append("Ouro em alta forte")
    
    if platform_risk > 0:
        alerts.append("Risco em plataforma detectado")
    
    return {
        "categoria": "Risco Macro e Plataforma",
        "pontuacao": round(raw_score, 1),
        "max_pontuacao": 11.0,
        "peso": 0.30,
        "pontuacao_ponderada": round(raw_score * 0.30, 2),
        "alertas": alerts if alerts else ["Indicadores macro e plataformas normais"]
    }

def calculate_direct_financial_risk() -> Dict[str, Any]:
    """
    Calcula o risco financeiro direto.
    
    Pontuação máxima: 21 pontos
    Peso na ponderação estratégica: 0.35
    """
    # Valores fixos para teste inicial - exemplo com riscos altos
    health_factor = 1.13  # +5 pontos para HF 1.10-1.15
    leverage = 3.2  # +5 pontos para Alavancagem > 3X
    wbtc_supply_abnormal = 0  # +3 pontos se anormal
    wbtc_parity = 0  # Max +7 pontos conforme % de descolamento
    
    # Cálculo das pontuações conforme escalas
    if health_factor < 1.10:
        hf_score = 7
    elif health_factor < 1.15:
        hf_score = 5
    elif health_factor < 1.30:
        hf_score = 3
    elif health_factor < 1.50:
        hf_score = 2
    else:
        hf_score = 0
    
    if leverage > 3.0:
        leverage_score = 5
    elif leverage > 2.0:
        leverage_score = 4
    elif leverage > 1.5:
        leverage_score = 2
    else:
        leverage_score = 1
    
    raw_score = hf_score + leverage_score + wbtc_supply_abnormal + wbtc_parity
    
    # Criar alertas para os riscos detectados
    alerts = []
    if hf_score >= 3:
        alerts.append(f"HF crítico: {health_factor}")
    
    if leverage_score >= 4:
        alerts.append(f"Alavancagem elevada: {leverage}x")
    
    if wbtc_supply_abnormal > 0:
        alerts.append("Supply WBTC anormal")
    
    if wbtc_parity > 0:
        alerts.append("Paridade WBTC-BTC descolada")
    
    return {
        "categoria": "Risco Financeiro Direto",
        "pontuacao": round(raw_score, 1),
        "max_pontuacao": 21.0,
        "peso": 0.35,
        "pontuacao_ponderada": round(raw_score * 0.35, 2),
        "alertas": alerts if alerts else ["Métricas financeiras saudáveis"]
    }

def get_risk_classification(score: float) -> Dict[str, str]:
    """
    Determina a classificação do risco com base na pontuação normalizada (0-10)
    
    Args:
        score: Pontuação normalizada entre 0 e 10
        
    Returns:
        Dicionário com classificação, emoji e descrição
    """
    if score < 2:
        return {
            "classificacao": "Risco Muito Baixo",
            "emoji": "✅",
            "descricao": "Posição extremamente segura, operar normalmente."
        }
    elif score < 4:
        return {
            "classificacao": "Risco Controlado",
            "emoji": "✅",
            "descricao": "Risco administrável, monitorar regularmente."
        }
    elif score < 6:
        return {
            "classificacao": "Risco Elevado",
            "emoji": "⚠️",
            "descricao": "Atenção redobrada, considerar redução de exposição."
        }
    elif score < 8:
        return {
            "classificacao": "Risco Crítico",
            "emoji": "🔴",
            "descricao": "Reduzir exposição imediatamente, monitorar 24/7."
        }
    else:
        return {
            "classificacao": "Risco Extremo",
            "emoji": "💀",
            "descricao": "Reduzir máximo possível da exposição, risco sistêmico alto."
        }

def get_risk_executive_summary(normalized_score: float, risk_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gera um resumo executivo baseado na pontuação de risco normalizada
    
    Args:
        normalized_score: Pontuação normalizada (0-10)
        risk_blocks: Lista com blocos de risco calculados
        
    Returns:
        Dicionário contendo o resumo executivo
    """
    classification = get_risk_classification(normalized_score)
    
    # Identificar principais riscos
    main_risks = []
    for block in risk_blocks:
        if block["pontuacao"] > 0 and len(block["alertas"]) > 0 and block["alertas"][0] != f"Sem alertas {block['categoria'].lower()}":
            main_risks.append(f"{block['categoria']} ({', '.join(block['alertas'])})")
    
    if not main_risks:
        main_risks.append("Nenhum risco significativo detectado")
    
    return {
        "titulo": "📝 Resumo gerencial do risco",
        "pontuacao": f"Pontuação Final Normalizada: {normalized_score:.2f} / 10",
        "classificacao": f"{classification['emoji']} {classification['classificacao']}",
        "descricao": classification['descricao'],
        "principais_riscos": main_risks,
        "observacao_estrategica": "Monitorar especialmente os componentes de maior peso na análise de risco."
    }

def get_consolidated_risk_analysis() -> Dict[str, Any]:
    """
    Realiza a análise de risco completa, calculando todos os componentes 
    e consolidando em uma pontuação final normalizada.
    
    Returns:
        Dicionário contendo todos os componentes da análise de risco
    """
    # Calcular os blocos de risco
    technical_risk = calculate_technical_risk()
    structural_risk = calculate_btc_structural_risk()
    macro_platform_risk = calculate_macro_platform_risk()
    financial_risk = calculate_direct_financial_risk()
    
    # Lista com todos os blocos calculados
    risk_blocks = [technical_risk, structural_risk, macro_platform_risk, financial_risk]
    
    # Calcular pontuação consolidada (soma dos valores ponderados)
    consolidated_score = sum(block["pontuacao_ponderada"] for block in risk_blocks)
    
    # Normalizar para escala 0-10 (máximo teórico é 14.1)
    theoretical_max = 14.1
    normalized_score = round((consolidated_score / theoretical_max) * 10, 2)
    
    # Obter resumo executivo
    executive_summary = get_risk_executive_summary(normalized_score, risk_blocks)
    
    # Montar resultado completo
    return {
        "blocos_risco": risk_blocks,
        "pontuacao_consolidada": consolidated_score,
        "pontuacao_normalizada": normalized_score,
        "resumo_executivo": executive_summary
    }