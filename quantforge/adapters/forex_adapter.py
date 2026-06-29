import os
from quantforge.adapters.base import DataAdapter
from quantforge.core.models import Bar
from typing import AsyncIterator


class ForexAdapter(DataAdapter):
    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.environ.get("ALPHA_VANTAGE_KEY", "demo")

    async def get_bars(self, symbol: str, start: str, end: str, timeframe: str) -> AsyncIterator[Bar]:
        raise NotImplementedError("ForexAdapter not yet implemented")
        yield
