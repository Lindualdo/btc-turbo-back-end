# app/routers/btc_emas.py

from fastapi import APIRouter, Depends, HTTPException
from tvDatafeed import TvDatafeed
from app.dependencies import get_tv_client
from app.config import get_settings, Settings
from pydantic import BaseModel
from typing import List
import pandas as pd
import logging

router = APIRouter()

class EMAData(BaseModel):
    interval: str
    current_price: float
    current_volume: float
    ema: float

async def _calculate_emas(tv: TvDatafeed, settings: Settings) -> List[EMAData]:
    print("🔥 running updated get_emas at", __file__)
    intervals = {"15m": "15", "1h": "60", "4h": "240", "1d": "D", "1w": "W"}
    periods = [17, 34, 144, 305, 610]
    results: List[EMAData] = []

    for interval_name, interval in intervals.items():
        try:
            df = tv.get_hist(
                symbol=settings.TV_SYMBOL,
                exchange=settings.TV_EXCHANGE,
                interval=interval,
                n_bars=max(periods) + 1
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao consultar TradingView: {str(e)}")

        if not isinstance(df, pd.DataFrame):
            raise HTTPException(status_code=502, detail=f"Retorno inválido do TradingView para {interval_name}: {df}")

        if df.empty or "close" not in df.columns:
            raise HTTPException(status_code=500, detail=f"Dados insuficientes para intervalo {interval_name}")

        try:
            ema_series = df["close"].ewm(span=periods[-1], adjust=False).mean()
            price_val = float(df["close"].iloc[-1])
            volume_val = float(df["volume"].iloc[-1]) if "volume" in df.columns else 0.0

            results.append(
                EMAData(
                    interval=interval_name,
                    current_price=price_val,
                    current_volume=volume_val,
                    ema=float(ema_series.iloc[-1])
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao calcular EMA para {interval_name}: {str(e)}")

    return results

@router.get("", response_model=List[EMAData], summary="Calcula EMAs (v1)", tags=["EMAs"])
async def get_emas_v1(
    tv: TvDatafeed = Depends(get_tv_client),
    settings: Settings = Depends(get_settings),
) -> List[EMAData]:
    return await _calculate_emas(tv, settings)

@router.get("/v2", response_model=List[EMAData], summary="Calcula EMAs (v2)", tags=["EMAs"])
async def get_emas_v2(
    tv: TvDatafeed = Depends(get_tv_client),
    settings: Settings = Depends(get_settings),
) -> List[EMAData]:
    return await _calculate_emas(tv, settings)
