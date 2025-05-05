# app/config.py

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Aldo - BTC TURBO"
    APP_VERSION: str = "1.0.1"
    HOST: str = Field("0.0.0.0", description="Host address for Uvicorn")
    PORT: int = Field(8000, description="Port for Uvicorn server")

    # TradingView credentials (tvdatafeed)
    TV_USERNAME: str = Field(..., env="TV_USERNAME")
    TV_PASSWORD: str = Field(..., env="TV_PASSWORD")

    # Notion integration
    NOTION_TOKEN: str = Field(..., env="NOTION_TOKEN")
    NOTION_DATABASE_ID_EMA: str = Field(..., env="NOTION_DATABASE_ID_EMA")
    NOTION_DATABASE_ID_MACRO: str = Field(..., env="NOTION_DATABASE_ID_MACRO")

    # CoinMetrics API (free community tier)
    COINMETRICS_API_KEY: str = Field(..., env="COINMETRICS_API_KEY")

    # Indicator weights and thresholds
    WEIGHT_EMA_200: float = Field(0.25, description="Peso para BTC vs 200D EMA")
    WEIGHT_REALIZED_PRICE: float = Field(0.25, description="Peso para Realized Price")
    WEIGHT_PUELL_MULTIPLE: float = Field(0.20, description="Peso para Puell Multiple")
    WEIGHT_BTC_DOMINANCE: float = Field(0.20, description="Peso para BTC Dominance")
    WEIGHT_MACRO_M2: float = Field(0.60, description="Peso para Macro M2 global")
    WEIGHT_MACRO_US10Y: float = Field(0.40, description="Peso para Macro US10Y yield")

    # Cache settings
    CACHE_EXPIRATION_SECONDS: int = Field(300, description="Tempo de expiração do cache em segundos")

    # TradingView default symbol
    TV_SYMBOL: str = Field("BTCUSDT", description="Símbolo usado nas chamadas ao TradingView")
    TV_EXCHANGE: str = Field("BINANCE", description="Exchange para consulta de dados")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna uma instância singleton das configurações carregadas do .env
    """
    return Settings()
