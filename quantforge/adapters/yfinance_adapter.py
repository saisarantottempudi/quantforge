from quantforge.adapters.base import DataAdapter
from quantforge.core.models import Bar
from typing import AsyncIterator


class YFinanceAdapter(DataAdapter):
    async def get_bars(self, symbol: str, start: str, end: str, timeframe: str) -> AsyncIterator[Bar]:
        raise NotImplementedError("YFinanceAdapter not yet implemented")
        yield  # make it an async generator
