from datetime import datetime

from quantforge.core.models import Bar, FeeConfig, Order, OrderSide, SlippageConfig
from quantforge.engine.broker import PaperBroker


def _bar(close: float = 100.0) -> Bar:
    return Bar(symbol="AAPL", ts=datetime(2024, 1, 2), o=close, h=close, l=close, c=close, v=1_000_000)


def test_market_buy_fills_at_close_no_slippage():
    broker = PaperBroker(SlippageConfig(model="fixed_bps", value=0), FeeConfig(model="percent", value=0))
    fill = broker.fill(Order(symbol="AAPL", side=OrderSide.BUY, qty=10), _bar(100.0))
    assert fill.fill_price == 100.0
    assert fill.fee == 0.0
    assert fill.qty == 10

def test_buy_slippage_fixed_bps_adds_cost():
    broker = PaperBroker(SlippageConfig(model="fixed_bps", value=10), FeeConfig(model="percent", value=0))
    fill = broker.fill(Order(symbol="AAPL", side=OrderSide.BUY, qty=1), _bar(100.0))
    assert abs(fill.fill_price - 100.1) < 0.001  # 10bps = 0.1%

def test_sell_slippage_reduces_price():
    broker = PaperBroker(SlippageConfig(model="fixed_bps", value=10), FeeConfig(model="percent", value=0))
    fill = broker.fill(Order(symbol="AAPL", side=OrderSide.SELL, qty=1), _bar(100.0))
    assert fill.fill_price < 100.0

def test_fee_percent():
    broker = PaperBroker(SlippageConfig(model="fixed_bps", value=0), FeeConfig(model="percent", value=0.001))
    fill = broker.fill(Order(symbol="AAPL", side=OrderSide.BUY, qty=10), _bar(100.0))
    assert abs(fill.fee - 1.0) < 0.001  # 10 * 100 * 0.001

def test_fee_flat():
    broker = PaperBroker(SlippageConfig(model="fixed_bps", value=0), FeeConfig(model="flat_per_trade", value=5.0))
    fill = broker.fill(Order(symbol="AAPL", side=OrderSide.BUY, qty=100), _bar(100.0))
    assert fill.fee == 5.0

def test_fill_order_id_matches():
    broker = PaperBroker(SlippageConfig(model="fixed_bps", value=0), FeeConfig(model="percent", value=0))
    order = Order(symbol="AAPL", side=OrderSide.BUY, qty=5)
    fill = broker.fill(order, _bar())
    assert fill.order_id == order.order_id
