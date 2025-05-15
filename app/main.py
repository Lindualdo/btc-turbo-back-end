# app/main.py

import logging
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.config import get_settings, Settings
from app.routers import analise_ciclos, analise_tecnica_emas, analise_fundamentos, analise_riscos, analise_tecnica_rsi, analise_divergencia_rsi, analise_tendencia_risco

# ⍅ Ativar logs nível INFO
logging.basicConfig(level=logging.INFO)

# Carrega configurações globais
settings: Settings = get_settings()

# Instancia a API com metadados
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de indicadores técnicos e de ciclos do BTC",
    contact={"name": "Equipe BTC Turbo", "email": "contato@btcturbo.com"},
)

# Tratamento genérico de exceções
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})

# Endpoint de saúde da API
@app.get("/health", summary="Health Check", tags=["Debug"])
async def health():
    return {"status": "ok"}

# Endpoint para exibir configurações carregadas
@app.get("/config", summary="Configurações Ativas", tags=["Debug"])
async def get_config(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "host": settings.HOST,
        "port": settings.PORT,
        "tv_symbol": settings.TV_SYMBOL,
        "cache_ttl": settings.CACHE_EXPIRATION_SECONDS
    }

# Registro dos routers com prefixo versionado
app.include_router(analise_tecnica_emas.router, prefix="/api/v1")
app.include_router(analise_ciclos.router, prefix="/api/v1")
app.include_router(analise_fundamentos.router, prefix="/api/v1")
app.include_router(analise_riscos.router, prefix="/api/v1")
app.include_router(analise_tecnica_rsi.router, prefix="/api/v1")
app.include_router(analise_divergencia_rsi.router, prefix="/api/v1")
app.include_router(analise_tendencia_risco.router, prefix="/api/v1")