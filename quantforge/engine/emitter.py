from collections.abc import AsyncIterator

from quantforge.adapters.base import DataAdapter
from quantforge.core.models import Bar, SessionConfig


class BarEmitter:
    def __init__(self, adapter: DataAdapter, config: SessionConfig):
        self._adapter = adapter
        self._config = config

    async def emit(self) -> AsyncIterator[Bar]:
        all_bars: list[Bar] = []
        for symbol in self._config.symbols:
            async for bar in self._adapter.get_bars(
                symbol=symbol,
                start=self._config.start,
                end=self._config.end,
                timeframe=self._config.timeframe,
            ):
                all_bars.append(bar)
        all_bars.sort(key=lambda b: b.ts)
        for bar in all_bars:
            yield bar
