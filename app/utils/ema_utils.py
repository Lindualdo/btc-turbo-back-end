import pandas as pd

def calcular_emas(df: pd.DataFrame, periods: list[int]) -> pd.DataFrame:
    for period in periods:
        df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    return df
