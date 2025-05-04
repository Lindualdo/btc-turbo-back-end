import logging
from tvDatafeed import TvDatafeed
from app.config import get_settings

_tv_instance = None  # cache global da sessão

def get_tv_instance():
    global _tv_instance

    if _tv_instance is not None:
        logging.info(f"♻️ Reutilizando sessão TV (ID={id(_tv_instance)})")
        return _tv_instance

    settings = get_settings()
    username = settings.TV_USERNAME
    password = settings.TV_PASSWORD

    try:
        logging.info("🚀 Iniciando nova sessão com TradingView...")
        logging.info(f"🔐 Username carregado: {username} | Senha definida? {'✅' if password else '❌'}")

        _tv_instance = TvDatafeed(username=username, password=password)

        # Validação de login (sem usar métodos inexistentes)
        if _tv_instance.username:
            logging.info(f"✅ Sessão TradingView autenticada como: {_tv_instance.username}")
        else:
            logging.warning("⚠️ Sessão anônima (nologin) ativa — dados limitados")

    except Exception as e:
        logging.error(f"❌ Falha ao conectar ou logar no TradingView: {e}")
        _tv_instance = None

    return _tv_instance
