from datetime import datetime

from quantforge.core.models import (
    AssetClass,
    Bar,
    Fill,
    Order,
    OrderSide,
    OrderType,
    SessionConfig,
)


def test_bar_default_asset_class():
    bar = Bar(symbol="AAPL", ts=datetime(2024, 1, 2), o=185.0, h=186.0, l=184.0, c=185.5, v=1_000_000)
    assert bar.asset_class == AssetClass.EQUITY


def test_order_generates_id():
    order = Order(symbol="AAPL", side=OrderSide.BUY, qty=10)
    assert len(order.order_id) == 36  # UUID length
    assert order.order_type == OrderType.MARKET


def test_order_limit_requires_no_auto_id():
    o1 = Order(symbol="AAPL", side=OrderSide.BUY, qty=10)
    o2 = Order(symbol="AAPL", side=OrderSide.BUY, qty=10)
    assert o1.order_id != o2.order_id


def test_fill_fields():
    fill = Fill(
        order_id="abc", symbol="AAPL", side=OrderSide.BUY,
        qty=10, fill_price=185.9, fee=1.0, ts=datetime(2024, 1, 2),
    )
    assert fill.fee == 1.0
    assert fill.fill_price == 185.9


def test_session_config_defaults():
    cfg = SessionConfig(symbols=["AAPL"], start="2024-01-01", end="2024-12-31")
    assert cfg.capital == 100_000.0
    assert cfg.portfolio_tick_interval == 1
    assert cfg.data_adapter == "yfinance"
