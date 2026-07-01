from collections.abc import AsyncIterator
from datetime import UTC, datetime

import ccxt.async_support as ccxt

from quantforge.adapters.base import DataAdapter
from quantforge.core.models import AssetClass, Bar


class CCXTAdapter(DataAdapter):
    def __init__(self, exchange_id: str = "binance"):
        self._exchange_id = exchange_id

    async def get_bars(
        self, symbol: str, start: str, end: str, timeframe: str
    ) -> AsyncIterator[Bar]:
        exchange_class = getattr(ccxt, self._exchange_id)
        exchange = exchange_class()
        try:
            since = int(datetime.fromisoformat(start).replace(tzinfo=UTC).timestamp() * 1000)
            end_ms = int(datetime.fromisoformat(end).replace(tzinfo=UTC).timestamp() * 1000)
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            for candle in ohlcv:
                if candle[0] > end_ms:
                    break
                yield Bar(
                    symbol=symbol,
                    ts=datetime.fromtimestamp(candle[0] / 1000, tz=UTC).replace(tzinfo=None),
                    o=candle[1], h=candle[2], l=candle[3], c=candle[4], v=candle[5],
                    asset_class=AssetClass.CRYPTO,
                )
        finally:
            await exchange.close()
