import os
from collections.abc import AsyncIterator
from datetime import datetime

import httpx

from quantforge.adapters.base import DataAdapter
from quantforge.core.models import AssetClass, Bar

_BASE = "https://www.alphavantage.co/query"


class ForexAdapter(DataAdapter):
    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.environ.get("ALPHA_VANTAGE_KEY", "demo")

    async def get_bars(
        self, symbol: str, start: str, end: str, timeframe: str
    ) -> AsyncIterator[Bar]:
        from_sym, to_sym = symbol.split("/")
        async with httpx.AsyncClient() as client:
            resp = await client.get(_BASE, params={
                "function": "FX_DAILY",
                "from_symbol": from_sym,
                "to_symbol": to_sym,
                "apikey": self._api_key,
                "outputsize": "full",
            })
            resp.raise_for_status()
            series = resp.json().get("Time Series FX (Daily)", {})
        for date_str, values in sorted(series.items()):
            if date_str < start or date_str > end:
                continue
            yield Bar(
                symbol=symbol,
                ts=datetime.fromisoformat(date_str),
                o=float(values["1. open"]),
                h=float(values["2. high"]),
                l=float(values["3. low"]),
                c=float(values["4. close"]),
                v=0.0,
                asset_class=AssetClass.FOREX,
            )
