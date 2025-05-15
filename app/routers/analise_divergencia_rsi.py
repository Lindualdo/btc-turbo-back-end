from app.services.tv_session_manager import get_tv_instance

from fastapi import APIRouter, HTTPException, Depends
from tvDatafeed import TvDatafeed, Interval
from app.utils.rsi_utils import calcular_rsi
from app.utils.divergence_utils import detectar_divergencias, consolidar_analise_divergencias
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

@router.get("/analise-divergencia-rsi", 
            summary="Análise de Divergências do RSI/IFR", 
            tags=["Análise Técnica"])
def get_all_divergences(settings: Settings = Depends(get_settings)):
    try:
        tv = get_tv_instance()
        result = {"divergencias": {}}
        todas_divergencias = {}

        for key, interval in interval_map.items():
            try:
                df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=interval, n_bars=500)

                if not isinstance(df, pd.DataFrame) or df.empty:
                    raise ValueError(f"Sem dados retornados para o intervalo {key}")

                # Calcular RSI
                df = calcular_rsi(df, periodo=14)
                
                # Detectar divergências
                analise = detectar_divergencias(df)
                result["divergencias"][key] = analise
                todas_divergencias[key] = analise

            except Exception as e:
                result["divergencias"][key] = {
                    "divergencia_detectada": False,
                    "erro": str(e)
                }

        # Adicionar análise consolidada
        result["consolidado"] = consolidar_analise_divergencias(todas_divergencias)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar com TradingView: {str(e)}")