# app/routers/analise_tecnica_rsi.py

from app.services.tv_session_manager import get_tv_instance
from fastapi import APIRouter, HTTPException, Depends
from tvDatafeed import TvDatafeed, Interval
from app.utils.rsi_utils import calcular_rsi, consolidar_analise_rsi
from app.config import Settings, get_settings
import pandas as pd
from typing import Dict, Any

router = APIRouter()

interval_map = {
    "15m": Interval.in_15_minute,
    "30m": Interval.in_30_minute,
    "1h": Interval.in_1_hour,
    "4h": Interval.in_4_hour,
    "1d": Interval.in_daily,
    "1w": Interval.in_weekly
}

rsi_periodo = 14

@router.get("/analise-tecnica-rsi", 
            summary="Análise Técnica BTC – RSI/IFR", 
            tags=["Análise Técnica"])
def get_all_rsi(settings: Settings = Depends(get_settings)):
    try:
        tv = get_tv_instance()
        result = {"rsi": {}}
        rsi_values = {}

        for key, interval in interval_map.items():
            try:
                df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=interval, n_bars=500)

                if not isinstance(df, pd.DataFrame) or df.empty:
                    raise ValueError(f"Sem dados retornados para o intervalo {key}")

                df = calcular_rsi(df, periodo=rsi_periodo)
                latest = df.iloc[-1]
                
                if "RSI" in latest and not pd.isna(latest["RSI"]):
                    rsi_value = latest["RSI"]
                    rsi_values[key] = rsi_value
                    result["rsi"][key] = {
                        "valor": round(rsi_value, 2)
                    }
                else:
                    result["rsi"][key] = {
                        "valor": None,
                        "erro": "RSI não disponível"
                    }

            except Exception as e:
                result["rsi"][key] = {
                    "valor": None,
                    "erro": str(e)
                }

        # Adicionar análise consolidada
        result["consolidado"] = consolidar_analise_rsi(rsi_values)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar com TradingView: {str(e)}")