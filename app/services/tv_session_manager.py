# app/services/tv_session_manager.py

from tvDatafeed import TvDatafeed
from app.config import get_settings
import logging

_tv_instance = None

def get_tv_instance():
    global _tv_instance

    if _tv_instance is not None:
        logging.info("✔️ Reutilizando sessão ativa com TradingView.")
        print(f"[tv_instance ID] {id(_tv_instance)}")
        return _tv_instance

    settings = get_settings()

    try:
        logging.info("🚀 Iniciando nova sessão com TradingView...")
        _tv_instance = TvDatafeed(
            username=settings.TV_USERNAME,
            password=settings.TV_PASSWORD
        )
        logging.info("✅ Sessão TradingView iniciada com sucesso.")
        print(f"[tv_instance ID] {id(_tv_instance)}")
    except Exception as e:
        logging.error(f"❌ Erro ao conectar com TradingView: {e}")
        _tv_instance = None

    return _tv_instance
