# app/services/tv_session_manager.py

from tvDatafeed import TvDatafeed
from app.config import get_settings
import logging

_tv_instance = None

def get_tv_instance():
    global _tv_instance
    settings = get_settings()

    if _tv_instance is not None:
        logging.info(f"♻️ Reutilizando sessão TV (ID={id(_tv_instance)})")
        return _tv_instance

    try:
        logging.info("🚀 Iniciando nova sessão com TradingView...")
        logging.info(f"🔐 Username carregado: {settings.TV_USERNAME} | Senha definida? {'✔️' if settings.TV_PASSWORD else '❌'}")

        _tv_instance = TvDatafeed(
            username=settings.TV_USERNAME,
            password=settings.TV_PASSWORD
        )

        # Testar se está logado de verdade
        user_info = _tv_instance.get_user_settings()
        if user_info:
            logging.info(f"✅ Login bem-sucedido! Sessão ativa como: {user_info}")
        else:
            logging.warning("⚠️ Sessão criada, mas sem dados do usuário. Pode estar em modo nologin.")

        logging.info(f"✅ Sessão TradingView iniciada (ID={id(_tv_instance)})")

    except Exception as e:
        logging.error(f"❌ Falha ao conectar ou logar no TradingView: {e}")
        _tv_instance = None

    return _tv_instance
