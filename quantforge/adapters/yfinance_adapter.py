import asyncio
from typing import AsyncIterator
import yfinance as yf
from quantforge.adapters.base import DataAdapter
from quantforge.core.models import AssetClass, Bar


class YFinanceAdapter(DataAdapter):
    async def get_bars(
        self, symbol: str, start: str, end: str, timeframe: str
    ) -> AsyncIterator[Bar]:
        ticker = yf.Ticker(symbol)
        df = await asyncio.to_thread(ticker.history, start=start, end=end, interval=timeframe)
        for ts, row in df.iterrows():
            yield Bar(
                symbol=symbol,
                ts=ts.to_pydatetime().replace(tzinfo=None),
                o=float(row["Open"]),
                h=float(row["High"]),
                l=float(row["Low"]),
                c=float(row["Close"]),
                v=float(row["Volume"]),
                asset_class=AssetClass.EQUITY,
            )
