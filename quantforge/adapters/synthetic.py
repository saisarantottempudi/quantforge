from datetime import datetime, timedelta
from typing import AsyncIterator
from quantforge.adapters.base import DataAdapter
from quantforge.core.models import Bar


class SyntheticAdapter(DataAdapter):
    def __init__(self, base_price: float = 100.0, num_bars: int = 10):
        self._base_price = base_price
        self._num_bars = num_bars

    async def get_bars(
        self, symbol: str, start: str, end: str, timeframe: str
    ) -> AsyncIterator[Bar]:
        price = self._base_price
        ts = datetime.fromisoformat(start)
        for i in range(self._num_bars):
            price = price * 1.001
            yield Bar(
                symbol=symbol,
                ts=ts + timedelta(days=i),
                o=price,
                h=round(price * 1.005, 4),
                l=round(price * 0.995, 4),
                c=price,
                v=1_000_000.0,
            )
