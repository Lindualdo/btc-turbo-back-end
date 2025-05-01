from fastapi import APIRouter
from tvDatafeed import TvDatafeed, Interval
from app.utils.ema_utils import calcular_emas

router = APIRouter()

interval_map = {
    "15m": Interval.in_15_minute,
    "1h": Interval.in_1_hour,
    "4h": Interval.in_4_hour,
    "1d": Interval.in_daily,
    "1w": Interval.in_weekly
}

emas_list = [17, 34, 144, 305, 610]

@router.get("/btc-emas")
def get_all_emas(username: str, password: str):
    try:
        tv = TvDatafeed(username=username, password=password)
        result = {"emas": {}}
        price = None
        volume = None

        for key, interval in interval_map.items():
            df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=interval, n_bars=500)
            df = calcular_emas(df, emas_list)
            latest = df.iloc[-1]

            if price is None:
                price = latest["close"]
                volume = latest["volume"]

            result["emas"][key] = {f"EMA_{p}": latest[f"EMA_{p}"] for p in emas_list}

        result["price"] = price
        result["volume"] = volume

        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}