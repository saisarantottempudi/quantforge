import pytest
from quantforge.engine.emitter import BarEmitter
from quantforge.adapters.synthetic import SyntheticAdapter
from quantforge.core.models import SessionConfig


def _config(symbols: list[str]) -> SessionConfig:
    return SessionConfig(
        symbols=symbols,
        start="2024-01-01",
        end="2024-01-10",
        data_adapter="synthetic",
    )


@pytest.mark.asyncio
async def test_emitter_yields_all_bars_single_symbol():
    adapter = SyntheticAdapter(num_bars=5)
    emitter = BarEmitter(adapter, _config(["AAPL"]))
    bars = [bar async for bar in emitter.emit()]
    assert len(bars) == 5

@pytest.mark.asyncio
async def test_emitter_merges_multi_symbol_sorted_by_ts():
    adapter = SyntheticAdapter(num_bars=3)
    emitter = BarEmitter(adapter, _config(["AAPL", "MSFT"]))
    bars = [bar async for bar in emitter.emit()]
    assert len(bars) == 6
    timestamps = [b.ts for b in bars]
    assert timestamps == sorted(timestamps)

@pytest.mark.asyncio
async def test_emitter_bar_symbols_correct():
    adapter = SyntheticAdapter(num_bars=2)
    emitter = BarEmitter(adapter, _config(["X", "Y"]))
    bars = [bar async for bar in emitter.emit()]
    symbols = {b.symbol for b in bars}
    assert symbols == {"X", "Y"}
