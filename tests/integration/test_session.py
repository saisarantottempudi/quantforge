import pytest

from quantforge.adapters.synthetic import SyntheticAdapter
from quantforge.core.models import Order, OrderSide, SessionConfig
from quantforge.engine.session_manager import SessionManager


@pytest.fixture
def config():
    return SessionConfig(
        symbols=["AAPL"],
        start="2024-01-01",
        end="2024-01-10",
        capital=10_000.0,
        data_adapter="synthetic",
    )


@pytest.mark.asyncio
async def test_session_runs_to_completion(config):
    adapter = SyntheticAdapter(num_bars=5)
    sm = SessionManager()
    session = sm.create(config, adapter)
    await session.run()
    assert session.status.value == "completed"


@pytest.mark.asyncio
async def test_session_emits_correct_bar_count(config):
    adapter = SyntheticAdapter(num_bars=3)
    sm = SessionManager()
    session = sm.create(config, adapter)
    await session.run()
    bars = []
    while not session.bar_queue.empty():
        bars.append(session.bar_queue.get_nowait())
    assert len(bars) == 3


@pytest.mark.asyncio
async def test_session_fills_submitted_order(config):
    adapter = SyntheticAdapter(num_bars=3)
    sm = SessionManager()
    session = sm.create(config, adapter)
    session.submit_order(Order(symbol="AAPL", side=OrderSide.BUY, qty=1))
    await session.run()
    fills = session.fills()
    assert len(fills) == 1
    assert fills[0]["symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_session_report_contains_all_keys(config):
    adapter = SyntheticAdapter(num_bars=5)
    sm = SessionManager()
    session = sm.create(config, adapter)
    await session.run()
    report = session.report()
    for key in ("sharpe", "max_drawdown", "var_95", "var_99", "total_pnl", "trades", "equity_curve"):
        assert key in report


def test_session_manager_get_and_delete():
    sm = SessionManager()
    config = SessionConfig(symbols=["X"], start="2024-01-01", end="2024-01-31", data_adapter="synthetic")
    session = sm.create(config, SyntheticAdapter())
    assert sm.get(session.session_id) is session
    assert sm.delete(session.session_id) is True
    assert sm.get(session.session_id) is None
