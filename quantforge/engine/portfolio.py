import math

from quantforge.core.models import Fill, OrderSide, Position


class PortfolioTracker:
    def __init__(self, capital: float):
        self.cash = capital
        self.positions: dict[str, Position] = {}
        self._equity_curve: list[float] = [capital]
        self._returns: list[float] = []

    def apply_fill(self, fill: Fill) -> None:
        notional = fill.qty * fill.fill_price
        if fill.side == OrderSide.BUY:
            self.cash -= notional + fill.fee
            if fill.symbol in self.positions:
                pos = self.positions[fill.symbol]
                total_cost = pos.qty * pos.avg_cost + notional
                new_qty = pos.qty + fill.qty
                self.positions[fill.symbol] = Position(
                    symbol=fill.symbol, qty=new_qty, avg_cost=total_cost / new_qty
                )
            else:
                self.positions[fill.symbol] = Position(
                    symbol=fill.symbol, qty=fill.qty, avg_cost=fill.fill_price
                )
        else:
            self.cash += notional - fill.fee
            pos = self.positions[fill.symbol]
            new_qty = pos.qty - fill.qty
            if new_qty <= 0:
                del self.positions[fill.symbol]
            else:
                self.positions[fill.symbol] = Position(
                    symbol=fill.symbol, qty=new_qty, avg_cost=pos.avg_cost
                )

    def update_prices(self, prices: dict[str, float]) -> float:
        equity = self.cash
        for symbol, pos in self.positions.items():
            equity += pos.qty * prices.get(symbol, pos.avg_cost)
        prev = self._equity_curve[-1]
        self._equity_curve.append(equity)
        if prev > 0:
            self._returns.append((equity - prev) / prev)
        return equity

    def sharpe(self, risk_free_rate: float = 0.0) -> float:
        if len(self._returns) < 2:
            return 0.0
        avg = sum(self._returns) / len(self._returns)
        variance = sum((r - avg) ** 2 for r in self._returns) / len(self._returns)
        std = math.sqrt(variance)
        if std == 0:
            return 0.0
        return (avg - risk_free_rate) / std * math.sqrt(252)

    def max_drawdown(self) -> float:
        peak = self._equity_curve[0]
        max_dd = 0.0
        for equity in self._equity_curve:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak if peak > 0 else 0.0
            max_dd = max(max_dd, dd)
        return max_dd

    def var(self, confidence: float = 0.95) -> float:
        if not self._returns:
            return 0.0
        sorted_r = sorted(self._returns)
        index = int((1 - confidence) * len(sorted_r))
        return -sorted_r[max(0, index)]

    def total_pnl(self) -> float:
        return self._equity_curve[-1] - self._equity_curve[0]

    def snapshot(self) -> dict:
        return {
            "equity": self._equity_curve[-1],
            "cash": self.cash,
            "pnl": self.total_pnl(),
            "positions": {
                s: {"qty": p.qty, "avg_cost": p.avg_cost}
                for s, p in self.positions.items()
            },
        }
