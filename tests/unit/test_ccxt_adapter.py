import pytest
from unittest.mock import AsyncMock, patch
from quantforge.adapters.ccxt_adapter import CCXTAdapter
from quantforge.core.models import AssetClass


MOCK_OHLCV = [
    [1704153600000, 42000.0, 43000.0, 41500.0, 42500.0, 150.5],
    [1704240000000, 42500.0, 44000.0, 42000.0, 43500.0, 200.0],
]


@pytest.mark.asyncio
async def test_ccxt_adapter_yields_bars():
    with patch("quantforge.adapters.ccxt_adapter.ccxt") as mock_ccxt:
        mock_exchange = AsyncMock()
        mock_exchange.fetch_ohlcv.return_value = MOCK_OHLCV
        mock_exchange.close = AsyncMock()
        mock_ccxt.binance.return_value = mock_exchange
        adapter = CCXTAdapter(exchange_id="binance")
        bars = [b async for b in adapter.get_bars("BTC/USDT", "2024-01-01", "2024-12-31", "1d")]
    assert len(bars) == 2
    assert bars[0].symbol == "BTC/USDT"
    assert bars[0].asset_class == AssetClass.CRYPTO
    assert bars[0].o == 42000.0


@pytest.mark.asyncio
async def test_ccxt_adapter_closes_exchange():
    with patch("quantforge.adapters.ccxt_adapter.ccxt") as mock_ccxt:
        mock_exchange = AsyncMock()
        mock_exchange.fetch_ohlcv.return_value = MOCK_OHLCV
        mock_exchange.close = AsyncMock()
        mock_ccxt.binance.return_value = mock_exchange
        adapter = CCXTAdapter()
        _ = [b async for b in adapter.get_bars("BTC/USDT", "2024-01-01", "2024-12-31", "1d")]
    mock_exchange.close.assert_called_once()
