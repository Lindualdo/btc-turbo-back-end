# app/routers/analise_tecnica_emas.py

from app.services.tv_session_manager import get_tv_instance

from fastapi import APIRouter, HTTPException, Depends
from tvDatafeed import TvDatafeed, Interval
from app.utils.ema_utils import calcular_emas, analisar_timeframe, consolidar_scores
from app.config import Settings, get_settings
import pandas as pd

router = APIRouter()

interval_map = {
    "15m": Interval.in_15_minute,
    "1h": Interval.in_1_hour,
    "4h": Interval.in_4_hour,
    "1d": Interval.in_daily,
    "1w": Interval.in_weekly
}

emas_list = [17, 34, 144, 305, 610]

@router.get("/analise-tecnica-emas", 
            summary="Análise Técnica BTC — EMAs", 
            tags=["Análise Técnica"])
def get_all_emas(settings: Settings = Depends(get_settings)):
    try:
        tv = get_tv_instance()  # ✅ correto
        result = {"emas": {}}
        price = None
        volume = None
        analises = {}

        for key, interval in interval_map.items():
            try:
                df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=interval, n_bars=500)

                if not isinstance(df, pd.DataFrame) or df.empty:
                    raise ValueError(f"Sem dados retornados para o intervalo {key}")

                df = calcular_emas(df, emas_list)
                latest = df.iloc[-1]

                if price is None:
                    price = latest["close"]
                    volume = latest.get("volume", 0.0)

                precos_timeframe = latest["close"]
                emas_timeframe = {f"EMA_{p}": latest.get(f"EMA_{p}", None) for p in emas_list}

                analise = analisar_timeframe(precos_timeframe, emas_timeframe)
                analises[key] = analise

                result["emas"][key] = {
                    **emas_timeframe,
                    "analise": analise
                }

            except Exception as e:
                raise HTTPException(status_code=502, detail=f"Erro ao processar intervalo {key}: {str(e)}")

        result["preco_atual"] = price
        result["volume_atual"] = volume
        result["consolidado"] = consolidar_scores(analises)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar com TradingView: {str(e)}")
