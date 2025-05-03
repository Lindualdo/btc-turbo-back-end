# app/main.py
from fastapi import FastAPI, Depends
from app.config import get_settings, Settings
from app.routers import btc_emas, btc_cycles

# Instância da aplicação com metadados
settings = get_settings()
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para análise de ciclos do Bitcoin",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Eventos de ciclo de vida
@app.on_event("startup")
async def startup_event():
    # Aqui podemos iniciar conexões (e.g. Notion, Redis)
    print("Starting up services...")

@app.on_event("shutdown")
async def shutdown_event():
    # Fechar conexões ou limpar recursos
    print("Shutting down services...")

# Health check
@app.get("/health", tags=["Health"], summary="Verifica status da API")
async def health_check():
    return {"status": "ok"}

# Registrar routers com versionamento
app.include_router(
    btc_emas.router,
    prefix="/api/v1/btc-emas",
    tags=["EMAs"],
    dependencies=[Depends(get_settings)]
)
app.include_router(
    btc_cycles.router,
    prefix="/api/v1/btc-cycles",
    tags=["Cycles"],
    dependencies=[Depends(get_settings)]
)

# Exemplo de injeção de settings em endpoint
@app.get("/config", tags=["Debug"], summary="Retorna configurações ativas")
async def get_config(settings: Settings = Depends(get_settings)):
    return {
        "host": settings.HOST,
        "port": settings.PORT,
        "tv_symbol": settings.TV_SYMBOL,
        "cache_ttl": settings.CACHE_EXPIRATION_SECONDS
    }

# Executar uvicorn via CLI: uvicorn app.main:app --host ... --port ...
