# app/routers/btc_emas.py

from fastapi import APIRouter, HTTPException, Query
from tvDatafeed import TvDatafeed, Interval
from app.utils.ema_utils import calcular_emas
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

@router.get("/btc-emas", summary="Calcula EMAs do BTC", tags=["EMAs"])
def get_all_emas(
    username: str = Query(..., description="Usuário do TradingView"),
    password: str = Query(..., description="Senha do TradingView")
):
    try:
        tv = TvDatafeed(username=username, password=password)
        result = {"emas": {}}
        price = None
        volume = None

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

                result["emas"][key] = {f"EMA_{p}": latest.get(f"EMA_{p}", None) for p in emas_list}

            except Exception as e:
                raise HTTPException(status_code=502, detail=f"Erro ao processar intervalo {key}: {str(e)}")

        result["preco_atual"] = price
        result["volume_atual"] = volume

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar com TradingView: {str(e)}")
