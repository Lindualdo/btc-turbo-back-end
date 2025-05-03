# app/main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.config import get_settings, Settings
from app.routers import btc_emas, btc_cycles

# Carrega configurações
settings: Settings = get_settings()

# Instancia aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

# Tratador genérico para exceções não capturadas
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})

# Saúde da aplicação
@app.get("/health", summary="Health Check", tags=["Debug"])
async def health():
    return {"status": "ok"}

# Debug de configurações
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

# Inclui routers de APIs
app.include_router(
    btc_emas.router,
    prefix="/api/v1/btc-emas",
)
app.include_router(
    btc_cycles.router,
    prefix="/api/v1/btc-cycles",
)
