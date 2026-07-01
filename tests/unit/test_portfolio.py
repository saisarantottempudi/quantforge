from datetime import datetime

from quantforge.core.models import Fill, OrderSide
from quantforge.engine.portfolio import PortfolioTracker


def _fill(symbol: str, side: OrderSide, qty: float, price: float, fee: float = 0.0) -> Fill:
    return Fill(order_id="t", symbol=symbol, side=side, qty=qty, fill_price=price, fee=fee, ts=datetime(2024, 1, 2))


def test_buy_reduces_cash_and_opens_position():
    p = PortfolioTracker(10_000.0)
    p.apply_fill(_fill("AAPL", OrderSide.BUY, 10, 100.0))
    assert p.cash == 9_000.0
    assert p.positions["AAPL"].qty == 10
    assert p.positions["AAPL"].avg_cost == 100.0

def test_sell_increases_cash_and_closes_position():
    p = PortfolioTracker(10_000.0)
    p.apply_fill(_fill("AAPL", OrderSide.BUY, 10, 100.0))
    p.apply_fill(_fill("AAPL", OrderSide.SELL, 10, 110.0))
    # 10_000 - 10*100 (buy) + 10*110 (sell) = 10_100
    assert p.cash == 10_100.0
    assert "AAPL" not in p.positions

def test_partial_sell_reduces_qty():
    p = PortfolioTracker(10_000.0)
    p.apply_fill(_fill("AAPL", OrderSide.BUY, 10, 100.0))
    p.apply_fill(_fill("AAPL", OrderSide.SELL, 4, 100.0))
    assert p.positions["AAPL"].qty == 6

def test_fee_reduces_cash():
    p = PortfolioTracker(10_000.0)
    p.apply_fill(_fill("AAPL", OrderSide.BUY, 10, 100.0, fee=5.0))
    assert p.cash == 8_995.0

def test_max_drawdown():
    p = PortfolioTracker(10_000.0)
    p._equity_curve = [10_000.0, 12_000.0, 8_000.0, 9_000.0]
    dd = p.max_drawdown()
    assert abs(dd - (12_000 - 8_000) / 12_000) < 0.001

def test_sharpe_flat_equity_is_zero():
    p = PortfolioTracker(10_000.0)
    for _ in range(10):
        p.update_prices({})
    assert p.sharpe() == 0.0

def test_var_95_positive_loss():
    p = PortfolioTracker(10_000.0)
    p._returns = [-0.05, -0.03, -0.01, 0.01, 0.02, 0.03, 0.02, 0.01, 0.0, -0.02]
    assert p.var(0.95) > 0

def test_total_pnl():
    p = PortfolioTracker(10_000.0)
    p._equity_curve = [10_000.0, 11_500.0]
    assert p.total_pnl() == 1_500.0
