from quantforge.adapters.base import DataAdapter
from quantforge.core.models import Bar
from typing import AsyncIterator


class CCXTAdapter(DataAdapter):
    def __init__(self, exchange_id: str = "binance"):
        self._exchange_id = exchange_id

    async def get_bars(self, symbol: str, start: str, end: str, timeframe: str) -> AsyncIterator[Bar]:
        raise NotImplementedError("CCXTAdapter not yet implemented")
        yield
