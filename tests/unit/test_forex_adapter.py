from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from quantforge.adapters.forex_adapter import ForexAdapter
from quantforge.core.models import AssetClass

MOCK_RESPONSE = {
    "Time Series FX (Daily)": {
        "2024-01-02": {"1. open": "1.0950", "2. high": "1.1000", "3. low": "1.0900", "4. close": "1.0975"},
        "2024-01-03": {"1. open": "1.0975", "2. high": "1.1050", "3. low": "1.0950", "4. close": "1.1020"},
        "2023-12-31": {"1. open": "1.0800", "2. high": "1.0850", "3. low": "1.0750", "4. close": "1.0820"},
    }
}


@pytest.mark.asyncio
async def test_forex_adapter_yields_bars_in_range():
    with patch("quantforge.adapters.forex_adapter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_RESPONSE
        mock_resp.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_client

        adapter = ForexAdapter(api_key="test_key")
        bars = [b async for b in adapter.get_bars("EUR/USD", "2024-01-01", "2024-12-31", "1d")]

    assert len(bars) == 2  # 2023-12-31 excluded (before start)
    assert bars[0].symbol == "EUR/USD"
    assert bars[0].asset_class == AssetClass.FOREX
    assert bars[0].o == 1.0950
