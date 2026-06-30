import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
from quantforge.adapters.yfinance_adapter import YFinanceAdapter
from quantforge.core.models import AssetClass


def _mock_df():
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    return pd.DataFrame({
        "Open": [185.0, 186.0],
        "High": [186.0, 187.0],
        "Low": [184.0, 185.0],
        "Close": [185.5, 186.5],
        "Volume": [1_000_000, 1_100_000],
    }, index=index)


@pytest.mark.asyncio
async def test_yfinance_adapter_yields_bars():
    with patch("quantforge.adapters.yfinance_adapter.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = _mock_df()
        adapter = YFinanceAdapter()
        bars = [b async for b in adapter.get_bars("AAPL", "2024-01-02", "2024-01-03", "1d")]
    assert len(bars) == 2
    assert bars[0].symbol == "AAPL"
    assert bars[0].asset_class == AssetClass.EQUITY
    assert bars[0].o == 185.0
    assert bars[0].c == 185.5


@pytest.mark.asyncio
async def test_yfinance_adapter_passes_correct_params():
    with patch("quantforge.adapters.yfinance_adapter.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = _mock_df()
        adapter = YFinanceAdapter()
        _ = [b async for b in adapter.get_bars("MSFT", "2023-01-01", "2023-12-31", "1d")]
    mock_ticker.assert_called_once_with("MSFT")
    mock_ticker.return_value.history.assert_called_once_with(
        start="2023-01-01", end="2023-12-31", interval="1d"
    )
