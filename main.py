from fastapi import FastAPI
from app.routers import btc_emas, btc_cycles

app = FastAPI()

app.include_router(btc_emas.router)
app.include_router(btc_cycles.router)