import pytest
from quantforge.adapters.synthetic import SyntheticAdapter

@pytest.mark.asyncio
async def test_synthetic_emits_correct_count():
    adapter = SyntheticAdapter(num_bars=5)
    bars = []
    async for bar in adapter.get_bars("AAPL", "2024-01-01", "2024-01-10", "1d"):
        bars.append(bar)
    assert len(bars) == 5

@pytest.mark.asyncio
async def test_synthetic_bar_fields():
    adapter = SyntheticAdapter(base_price=100.0, num_bars=1)
    bars = []
    async for bar in adapter.get_bars("TEST", "2024-01-01", "2024-01-01", "1d"):
        bars.append(bar)
    b = bars[0]
    assert b.symbol == "TEST"
    assert b.h >= b.c >= b.l
    assert b.v > 0

@pytest.mark.asyncio
async def test_synthetic_timestamps_increase():
    adapter = SyntheticAdapter(num_bars=3)
    bars = []
    async for bar in adapter.get_bars("X", "2024-01-01", "2024-01-10", "1d"):
        bars.append(bar)
    assert bars[0].ts < bars[1].ts < bars[2].ts
