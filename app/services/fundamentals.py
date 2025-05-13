# app/services/fundamentals.py

import math
import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from requests.exceptions import HTTPError

COINGECKO_URL     = "https://api.coingecko.com/api/v3/coins/bitcoin"
COINMETRICS_BASE  = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
FRED_M2_CSV       = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=M2SL"

def _fetch_coingecko() -> dict:
    resp = requests.get(
        COINGECKO_URL,
        params={"localization": "false", "tickers": "false", "market_data": "true"}
    )
    resp.raise_for_status()
    md = resp.json().get("market_data", {})
    return {
        "price": md.get("current_price", {}).get("usd", 0),
        "supply": md.get("circulating_supply", 0)
    }

def _fetch_coinmetrics_timeseries(metric: str, days: int = 365) -> (float, float):
    now = datetime.utcnow()
    start = (now - timedelta(days=days)).isoformat()
    end   = now.isoformat()
    params = {
        "assets": "btc",
        "metrics": metric,
        "frequency": "1d",
        "start_time": start,
        "end_time": end
    }
    resp = requests.get(COINMETRICS_BASE, params=params)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    if len(data) >= 2:
        prev = float(data[0].get("value", 0))
        curr = float(data[-1].get("value", 0))
        return prev, curr
    raise ValueError(f"Not enough data for metric '{metric}'")

def get_model_variance() -> dict:
    try:
        from notion_client import Client
        from app.config import get_settings
        settings = get_settings()
        NOTION_TOKEN = settings.NOTION_TOKEN
        
        # Obter o ID do banco de dados e verificar se é válido
        DATABASE_ID = settings.NOTION_DATABASE_ID_MACRO.strip().replace('"', '')
        
        # Verificar se o DATABASE_ID não está vazio
        if not DATABASE_ID:
            logging.error("DATABASE_ID está vazio. Verifique a variável NOTION_DATABASE_ID_MACRO no arquivo .env")
            raise ValueError("DATABASE_ID não pode ser vazio.")
            
        logging.info(f"Model Variance - DATABASE_ID: {DATABASE_ID}")
        notion = Client(auth=NOTION_TOKEN)

        response = notion.databases.query(database_id=DATABASE_ID)
        for row in response["results"]:
            props = row["properties"]
            nome = props["indicador"]["title"][0]["plain_text"].strip().lower()
            if nome == "model_variance":
                valor = float(props["valor"]["number"])

                # Ajustando a lógica conforme a documentação
                if valor <= -1.4:
                    score = 3
                elif valor <= -0.8:
                    score = 2
                elif valor <= -0.3:
                    score = 1
                else:
                    score = 0

                peso = 0.35
                return {
                    "indicador": "Model Variance (S2F)",
                    "fonte": "Notion API",
                    "valor": round(valor, 2),
                    "pontuacao_bruta": score,
                    "peso": peso,
                    "pontuacao_ponderada": round((score / 3) * peso, 4)
                }

        raise ValueError("Indicador 'model_variance' não encontrado.")
    except Exception as e:
        peso = 0.35
        return {
            "indicador": "Model Variance (S2F)",
            "fonte": "Notion API",
            "valor": "erro",
            "pontuacao_bruta": 0,
            "peso": peso,
            "pontuacao_ponderada": 0.0,
            "erro": str(e)
        }

def get_mvrv_zscore() -> dict:
    peso = 0.25
    try:
        from notion_client import Client
        from app.config import get_settings
        settings = get_settings()
        NOTION_TOKEN = settings.NOTION_TOKEN
        
        # Obter o ID do banco de dados e verificar se é válido
        DATABASE_ID = settings.NOTION_DATABASE_ID_MACRO.strip().replace('"', '')
        
        # Verificar se o DATABASE_ID não está vazio
        if not DATABASE_ID:
            logging.error("DATABASE_ID está vazio. Verifique a variável NOTION_DATABASE_ID_MACRO no arquivo .env")
            raise ValueError("DATABASE_ID não pode ser vazio.")
            
        logging.info(f"MVRV Z-Score - DATABASE_ID: {DATABASE_ID}")
        notion = Client(auth=NOTION_TOKEN)

        response = notion.databases.query(database_id=DATABASE_ID)
        for row in response["results"]:
            props = row["properties"]
            nome = props["indicador"]["title"][0]["plain_text"].strip().lower()
            if nome == "mvrv":
                valor = float(props["valor"]["number"])

                # Atualizando as regras conforme documentação
                if valor < 2.0:
                    score = 2
                elif valor < 2.5:
                    score = 1.5
                elif valor < 5.0:
                    score = 1
                else:
                    score = 0

                return {
                    "indicador": "MVRV Z-Score",
                    "fonte": "Notion API",
                    "valor": round(valor, 2),
                    "pontuacao_bruta": score,
                    "peso": peso,
                    "pontuacao_ponderada": round((score / 3) * peso, 4)
                }

        raise ValueError("Indicador 'mvrv' não encontrado.")
    except Exception as e:
        return {
            "indicador": "MVRV Z-Score",
            "fonte": "Notion API",
            "valor": "erro",
            "pontuacao_bruta": 0,
            "peso": peso,
            "pontuacao_ponderada": 0.0,
            "erro": str(e)
        }

def get_vdd_multiple() -> dict:
    peso = 0.20
    try:
        from notion_client import Client
        from app.config import get_settings
        settings = get_settings()
        NOTION_TOKEN = settings.NOTION_TOKEN
        
        # Obter o ID do banco de dados e verificar se é válido
        DATABASE_ID = settings.NOTION_DATABASE_ID_MACRO.strip().replace('"', '')
        
        # Verificar se o DATABASE_ID não está vazio
        if not DATABASE_ID:
            logging.error("DATABASE_ID está vazio. Verifique a variável NOTION_DATABASE_ID_MACRO no arquivo .env")
            raise ValueError("DATABASE_ID não pode ser vazio.")
            
        logging.info(f"VDD Multiple - DATABASE_ID: {DATABASE_ID}")
        notion = Client(auth=NOTION_TOKEN)

        response = notion.databases.query(database_id=DATABASE_ID)
        for row in response["results"]:
            props = row["properties"]
            nome = props["indicador"]["title"][0]["plain_text"].strip().lower()
            if nome == "vdd_multiple":
                valor = float(props["valor"]["number"])

                # Atualizando as regras conforme documentação
                if valor < 1.0:
                    score = 2
                elif valor < 2.0:
                    score = 1
                else:
                    score = 0

                return {
                    "indicador": "VDD Multiple",
                    "fonte": "Notion API",
                    "valor": round(valor, 2),
                    "pontuacao_bruta": score,
                    "peso": peso,
                    "pontuacao_ponderada": round((score / 3) * peso, 4)
                }

        raise ValueError("Indicador 'vdd_multiple' não encontrado.")
    except Exception as e:
        return {
            "indicador": "VDD Multiple",
            "fonte": "Notion API",
            "valor": "erro",
            "pontuacao_bruta": 0,
            "peso": peso,
            "pontuacao_ponderada": 0.0,
            "erro": str(e)
        }

def get_global_m2_expansion() -> dict:
    peso = 0.20
    try:
        from notion_client import Client
        from app.config import get_settings
        settings = get_settings()
        NOTION_TOKEN = settings.NOTION_TOKEN
        
        # Obter o ID do banco de dados e verificar se é válido
        DATABASE_ID = settings.NOTION_DATABASE_ID_MACRO.strip().replace('"', '')
        
        # Verificar se o DATABASE_ID não está vazio
        if not DATABASE_ID:
            logging.error("DATABASE_ID está vazio. Verifique a variável NOTION_DATABASE_ID_MACRO no arquivo .env")
            raise ValueError("DATABASE_ID não pode ser vazio.")
            
        logging.info(f"Global M2 Expansion - DATABASE_ID: {DATABASE_ID}")
        notion = Client(auth=NOTION_TOKEN)

        response = notion.databases.query(database_id=DATABASE_ID)
        for row in response["results"]:
            props = row["properties"]
            nome = props["indicador"]["title"][0]["plain_text"].strip().lower()
            if nome == "m2_global":
                valor = float(props["valor"]["number"])

                # Atualizando as regras conforme documentação
                if valor > 3:
                    score = 2
                elif valor >= 1 and valor <= 3:
                    score = 1
                elif valor >= -1 and valor < 1:
                    score = 0
                else:  # Valor < -1
                    score = 0

                return {
                    "indicador": "Expansão Global M2 (6m)",
                    "fonte": "Notion API",
                    "valor": round(valor, 2),
                    "pontuacao_bruta": score,
                    "peso": peso,
                    "pontuacao_ponderada": round((score / 3) * peso, 4)
                }

        raise ValueError("Indicador 'm2_global' não encontrado.")
    except Exception as e:
        return {
            "indicador": "Expansão Global M2 (6m)",
            "fonte": "Notion API",
            "valor": "erro",
            "pontuacao_bruta": 0,
            "peso": peso,
            "pontuacao_ponderada": 0.0,
            "erro": str(e)
        }

def get_fundamentals_executive_summary(consolidado: float) -> dict:
    """
    Gera um resumo executivo com base na pontuação consolidada dos indicadores fundamentalistas.
    
    Args:
        consolidado: Pontuação consolidada (0-5)
        
    Returns:
        Dicionário contendo o resumo executivo formatado
    """
    # Determinar classificação com base na pontuação
    if consolidado <= 1.0:
        classificacao = "Muito Fraca"
        cor = "🔴"
        interpretacao = "Evitar qualquer exposição"
    elif consolidado <= 2.5:
        classificacao = "Fraca"
        cor = "🟠"
        interpretacao = "Operar apenas com setups muito seguros"
    elif consolidado <= 3.5:
        classificacao = "Moderada"
        cor = "🟡"
        interpretacao = "Risco controlado e seletividade"
    elif consolidado <= 4.4:
        classificacao = "Forte"
        cor = "🔵"
        interpretacao = "Operar com modelo de risco padrão"
    else:  # consolidado >= 4.5
        classificacao = "Muito Forte"
        cor = "🟢"
        interpretacao = "Operar com agressividade controlada"
    
    # Montar o resumo executivo
    resumo = {
        "titulo": "✅ Resumo Executivo - Tendência Fundamentalista BTC",
        "pontuacao": f"🎯 Pontuação Final: {consolidado} / 5.0",
        "classificacao": f"Classificação: {cor} {classificacao}",
        "interpretacao": interpretacao,
        "escala": {
            "titulo": "🔢 Escala de Avaliação (0 a 5)",
            "faixas": [
                {"faixa": "🔴 Muito Fraca", "pontuacao": "0.0 – 1.0", "cor": "Vermelho", "interpretacao": "Evitar qualquer exposição"},
                {"faixa": "🟠 Fraca", "pontuacao": "1.1 – 2.5", "cor": "Laranja", "interpretacao": "Operar apenas com setups muito seguros"},
                {"faixa": "🟡 Moderada", "pontuacao": "2.6 – 3.5", "cor": "Amarelo", "interpretacao": "Risco controlado e seletividade"},
                {"faixa": "🔵 Forte", "pontuacao": "3.6 – 4.4", "cor": "Azul", "interpretacao": "Operar com modelo de risco padrão"},
                {"faixa": "🟢 Muito Forte", "pontuacao": "4.5 – 5.0", "cor": "Verde", "interpretacao": "Operar com agressividade controlada"}
            ]
        }
    }
    
    return resumo

def get_all_fundamentals() -> dict:
    indicadores = [
        get_model_variance(),
        get_mvrv_zscore(),
        get_vdd_multiple(),
        get_global_m2_expansion()
    ]
    total_ponderado = sum(i["pontuacao_ponderada"] for i in indicadores)
    score_final = round((total_ponderado / 2) * 10, 2)  # normalização conforme doc
    
    # Converter score_final para escala 0-5 (já está em escala 0-10)
    score_final_5 = round(score_final / 2, 2)
    
    # Obter resumo executivo
    resumo = get_fundamentals_executive_summary(score_final_5)
    
    return {
        "tabela": indicadores, 
        "consolidado": score_final,
        "consolidado_5": score_final_5,
        "resumo_executivo": resumo
    }