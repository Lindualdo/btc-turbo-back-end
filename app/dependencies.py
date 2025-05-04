from app.services.tv_session_manager import get_tv_instance
# app/dependencies.py
from fastapi import Depends
from tvDatafeed import TvDatafeed
from notion_client import Client as NotionClient

from app.config import get_settings, Settings


def get_tv_client(settings: Settings = Depends(get_settings)) -> TvDatafeed:
    """
    Dependency that provides an authenticated TvDatafeed client using credentials from settings.
    """
    return TvDatafeed(
        username=settings.TV_USERNAME,
        password=settings.TV_PASSWORD
    )


def get_notion_client(settings: Settings = Depends(get_settings)) -> NotionClient:
    """
    Dependency that provides an authenticated Notion client using the integration token from settings.
    """
    return NotionClient(auth=settings.NOTION_TOKEN)