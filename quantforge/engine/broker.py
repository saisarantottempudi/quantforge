from quantforge.core.models import Bar, FeeConfig, Fill, Order, OrderSide, SlippageConfig


class PaperBroker:
    def __init__(self, slippage: SlippageConfig, fees: FeeConfig):
        self._slippage = slippage
        self._fees = fees

    def fill(self, order: Order, bar: Bar) -> Fill:
        fill_price = self._apply_slippage(order, bar.c)
        fee = self._apply_fees(order.qty, fill_price)
        return Fill(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            qty=order.qty,
            fill_price=fill_price,
            fee=fee,
            ts=bar.ts,
        )

    def _apply_slippage(self, order: Order, close_price: float) -> float:
        direction = 1 if order.side == OrderSide.BUY else -1
        if self._slippage.model == "fixed_bps":
            slip = close_price * (self._slippage.value / 10_000) * direction
        elif self._slippage.model == "percent":
            slip = close_price * self._slippage.value * direction
        else:
            slip = 0.0
        return close_price + slip

    def _apply_fees(self, qty: float, fill_price: float) -> float:
        if self._fees.model == "percent":
            return qty * fill_price * self._fees.value
        return self._fees.value  # flat_per_trade
