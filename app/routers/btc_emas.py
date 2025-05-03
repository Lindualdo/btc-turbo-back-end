# app/routers/btc_emas.py
from fastapi import APIRouter, Depends, HTTPException
from tvDatafeed import TvDatafeed
from app.dependencies import get_tv_client
from app.config import Settings, get_settings
from pydantic import BaseModel
from typing import List

router = APIRouter()

class EMAData(BaseModel):
    """
    Schema para representar os dados de EMA calculados.
    """
    interval: str
    current_price: float
    current_volume: float
    ema: float

@router.get("/", response_model=List[EMAData], summary="Calcula EMAs para vários períodos", tags=["EMAs"])
async def get_emas(
    tv: TvDatafeed = Depends(get_tv_client),
    settings: Settings = Depends(get_settings),
):
    """
    Busca histórico de preços no TradingView e calcula EMAs para os períodos definidos.
    """
    try:
        intervals = {"15m": "15", "1h": "60", "4h": "240", "1d": "D", "1w": "W"}
        periods = [17, 34, 144, 305, 610]
        results: List[EMAData] = []
        for interval_name, interval in intervals.items():
            df = tv.get_hist(
                symbol=settings.TV_SYMBOL,
                exchange=settings.TV_EXCHANGE,
                interval=interval,
                n_bars=max(periods) + 1
            )
            if df.empty or 'close' not in df.columns:
                raise HTTPException(status_code=500, detail=f"Dados insuficientes para intervalo {interval_name}")

            # Calcula EMA mais longa disponível
            ema_series = df['close'].ewm(span=periods[-1], adjust=False).mean()
            results.append(
                EMAData(
                    interval=interval_name,
                    current_price=float(df['close'].iloc[-1]),
                    current_volume=float(df.get('volume', pd.Series()).iloc[-1] if 'volume' in df.columns else 0.0),
                    ema=float(ema_series.iloc[-1])
                )
            )
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
