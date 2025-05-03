# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, AnyHttpUrl
from typing import List

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "BTC Cycle API"
    APP_VERSION: str = "1.0.0"
    HOST: str = Field("0.0.0.0", description="Host address for Uvicorn")
    PORT: int = Field(8000, description="Port for Uvicorn server")

    # TradingView credentials (tvdatafeed)
    TV_USERNAME: str = Field(..., env="TV_USERNAME")
    TV_PASSWORD: str = Field(..., env="TV_PASSWORD")

    # Notion integration
    NOTION_TOKEN: str = Field(..., env="NOTION_TOKEN")
    NOTION_DATABASE_ID_EMA: str = Field(..., env="NOTION_DATABASE_ID_EMA")
    NOTION_DATABASE_ID_MACRO: str = Field(..., env="NOTION_DATABASE_ID_MACRO")

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


def get_settings() -> Settings:
    """
    Retorna uma instância singleton das configurações carregadas do .env
    """
    return Settings()

# .env.example (colocar na raiz do projeto)
# COPIE este arquivo para `.env` e preencha as variáveis abaixo
#
# APP_NAME=BTC Cycle API
# APP_VERSION=1.0.0
# HOST=0.0.0.0
# PORT=8000
#
# TV_USERNAME=seu_usuario_tv
# TV_PASSWORD=sua_senha_tv
#
# NOTION_TOKEN=seu_token_notion
# NOTION_DATABASE_ID_EMA=seu_id_database_ema
# NOTION_DATABASE_ID_MACRO=seu_id_database_macro
#
# # Opcional: ajuste pesos conforme necessidade
# WEIGHT_EMA_200=0.25
# WEIGHT_REALIZED_PRICE=0.25
# WEIGHT_PUELL_MULTIPLE=0.20
# WEIGHT_BTC_DOMINANCE=0.20
# WEIGHT_MACRO_M2=0.60
# WEIGHT_MACRO_US10Y=0.40
#
# CACHE_EXPIRATION_SECONDS=300
#
# # TradingView defaults
# TV_SYMBOL=BTCUSDT
# TV_EXCHANGE=BINANCE
